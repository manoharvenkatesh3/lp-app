"""REST API endpoints for post-interview analytics.

This module provides FastAPI endpoints for accessing interview analytics,
scorecards, and export functionality with RBAC protection.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .analytics import InterviewAnalytics
from .auth import RBACManager, User, UserRole
from .database import AnalyticsDatabase, AuditLogger
from .models import (
    AnalyticsConfig,
    BackgroundTask,
    InterviewSession,
    ScoreCard,
    TaskStatus,
    TranscriptData,
)

# Security scheme
security = HTTPBearer()


def create_analytics_router(
    database: AnalyticsDatabase,
    rbac_manager: RBACManager,
    audit_logger: AuditLogger,
    analytics_engine: InterviewAnalytics,
    task_manager
) -> APIRouter:
    """Create FastAPI router for analytics endpoints."""
    
    router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
    
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get current authenticated user from JWT token."""
        token = credentials.credentials
        user = rbac_manager.get_user_from_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return user
    
    def require_permission(action: str, resource: str):
        """Decorator to require specific permission."""
        def permission_checker(current_user: User = Depends(get_current_user)):
            if not rbac_manager.has_permission(current_user, action, resource):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions for {action} on {resource}"
                )
            return current_user
        return permission_checker
    
    # Authentication endpoints
    @router.post("/auth/login")
    async def login(username: str, password: str):
        """Authenticate user and return JWT token."""
        user = rbac_manager.authenticate_user(username, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        token = rbac_manager.generate_token(user)
        
        # Log login
        await audit_logger.log_access(
            user_id=user.user_id,
            user_role=user.role,
            resource_type="auth",
            resource_id="login"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
    
    @router.post("/auth/logout")
    async def logout(current_user: User = Depends(get_current_user)):
        """Logout user (token invalidation handled client-side)."""
        await audit_logger.log_access(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="auth",
            resource_id="logout"
        )
        
        return {"message": "Successfully logged out"}
    
    # Scorecard endpoints
    @router.get("/scorecards/{session_id}")
    async def get_scorecard(
        session_id: str,
        current_user: User = Depends(require_permission("read", "scorecards"))
    ):
        """Get scorecard for a specific interview session."""
        # Check resource access
        if not rbac_manager.check_resource_access(current_user, "scorecards", session_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this scorecard"
            )
        
        scorecard = await database.get_scorecard(session_id)
        if not scorecard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scorecard not found"
            )
        
        # Log access
        await audit_logger.log_access(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="scorecards",
            resource_id=session_id,
            session_id=session_id
        )
        
        return JSONResponse(content=scorecard)
    
    @router.get("/scorecards/candidate/{candidate_id}")
    async def get_candidate_scorecards(
        candidate_id: str,
        current_user: User = Depends(require_permission("read", "scorecards"))
    ):
        """Get all scorecards for a candidate."""
        scorecards = await database.get_candidate_scorecards(candidate_id)
        
        # Filter based on user permissions
        if current_user.role == UserRole.INTERVIEWER:
            # Only return scorecards for sessions they conducted
            scorecards = [sc for sc in scorecards if sc.get("interviewer_id") == current_user.user_id]
        
        # Log access
        await audit_logger.log_access(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="scorecards",
            resource_id=f"candidate_{candidate_id}"
        )
        
        return {"scorecards": scorecards, "count": len(scorecards)}
    
    @router.get("/scorecards/job/{job_id}")
    async def get_job_scorecards(
        job_id: str,
        limit: int = Query(50, le=100),
        offset: int = Query(0, ge=0),
        current_user: User = Depends(require_permission("read", "scorecards"))
    ):
        """Get all scorecards for a job position."""
        scorecards = await database.get_job_scorecards(job_id)
        
        # Apply pagination
        paginated_scorecards = scorecards[offset:offset + limit]
        
        # Log access
        await audit_logger.log_access(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="scorecards",
            resource_id=f"job_{job_id}"
        )
        
        return {
            "scorecards": paginated_scorecards,
            "total": len(scorecards),
            "limit": limit,
            "offset": offset
        }
    
    @router.post("/scorecards/{session_id}/regenerate")
    async def regenerate_scorecard(
        session_id: str,
        job_requirements: List[str],
        current_user: User = Depends(require_permission("write", "scorecards"))
    ):
        """Regenerate scorecard for a session."""
        # Check resource access
        if not rbac_manager.check_resource_access(current_user, "scorecards", session_id, "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to modify this scorecard"
            )
        
        # Submit background task
        task_id = await task_manager.submit_task(
            task_type="analytics",
            session_id=session_id,
            task_data={"job_requirements": job_requirements}
        )
        
        # Log action
        await audit_logger.log_update(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="scorecards",
            resource_id=session_id,
            changes_made={"action": "regenerate", "job_requirements": job_requirements},
            session_id=session_id
        )
        
        return {
            "message": "Scorecard regeneration started",
            "task_id": task_id
        }
    
    # Export endpoints
    @router.post("/export/scorecards/{session_id}")
    async def export_scorecard(
        session_id: str,
        export_format: str = Query("json", regex="^(json|pdf)$"),
        current_user: User = Depends(require_permission("export", "scorecards"))
    ):
        """Export scorecard in specified format."""
        # Check resource access
        if not rbac_manager.check_resource_access(current_user, "scorecards", session_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this scorecard"
            )
        
        # Submit export task
        task_id = await task_manager.submit_task(
            task_type="export",
            session_id=session_id,
            task_data={
                "export_type": export_format,
                "resource_id": session_id,
                "resource_type": "scorecard"
            }
        )
        
        # Log export
        await audit_logger.log_access(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="exports",
            resource_id=f"{session_id}_{export_format}",
            session_id=session_id
        )
        
        return {
            "message": f"Export started in {export_format} format",
            "task_id": task_id
        }
    
    # Task management endpoints
    @router.get("/tasks/{task_id}")
    async def get_task_status(
        task_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get status of a background task."""
        task = await task_manager.get_task_status(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if user can access this task
        if not rbac_manager.check_resource_access(current_user, "tasks", task_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this task"
            )
        
        return task.dict()
    
    @router.get("/tasks/session/{session_id}")
    async def get_session_tasks(
        session_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get all tasks for a session."""
        # Check session access
        if not rbac_manager.check_resource_access(current_user, "sessions", session_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        tasks = await task_manager.get_user_tasks(session_id)
        return {"tasks": [task.dict() for task in tasks]}
    
    @router.post("/tasks/{task_id}/cancel")
    async def cancel_task(
        task_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Cancel a running task."""
        # Check task access and cancellation permissions
        if not rbac_manager.has_permission(current_user, "write", "tasks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to cancel tasks"
            )
        
        success = await task_manager.cancel_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or cannot be cancelled"
            )
        
        return {"message": "Task cancelled successfully"}
    
    # Analytics configuration endpoints
    @router.get("/config")
    async def get_analytics_config(
        current_user: User = Depends(require_permission("read", "analytics"))
    ):
        """Get analytics configuration."""
        # Return default config (in production, get from database)
        config = AnalyticsConfig()
        return config.dict()
    
    @router.put("/config")
    async def update_analytics_config(
        config: AnalyticsConfig,
        current_user: User = Depends(require_permission("write", "analytics"))
    ):
        """Update analytics configuration."""
        # Only admins can update config
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update configuration"
            )
        
        # Store config in database (implementation needed)
        
        # Log configuration change
        await audit_logger.log_update(
            user_id=current_user.user_id,
            user_role=current_user.role,
            resource_type="config",
            resource_id="analytics",
            changes_made=config.dict()
        )
        
        return {"message": "Configuration updated successfully"}
    
    # Audit endpoints
    @router.get("/audit/{resource_type}/{resource_id}")
    async def get_audit_trail(
        resource_type: str,
        resource_id: str,
        limit: int = Query(100, le=500),
        current_user: User = Depends(require_permission("view_audit", "all"))
    ):
        """Get audit trail for a resource."""
        # Only users with view_audit permission can access
        if not rbac_manager.has_permission(current_user, "view_audit", "all"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view audit logs"
            )
        
        audit_entries = await audit_logger.get_audit_trail(resource_type, resource_id, limit)
        return {
            "audit_trail": audit_entries,
            "total": len(audit_entries),
            "resource_type": resource_type,
            "resource_id": resource_id
        }
    
    # Statistics endpoints
    @router.get("/statistics")
    async def get_analytics_statistics(
        current_user: User = Depends(require_permission("read", "analytics"))
    ):
        """Get analytics processing statistics."""
        task_stats = task_manager.get_task_statistics()
        
        # Add database statistics if available
        db_stats = {}
        try:
            # Get total scorecards count
            if database.pool:
                async with database.pool.acquire() as conn:
                    total_scorecards = await conn.fetchval("SELECT COUNT(*) FROM scorecards")
                    total_sessions = await conn.fetchval("SELECT COUNT(*) FROM interview_sessions")
                    
                    db_stats = {
                        "total_scorecards": total_scorecards,
                        "total_sessions": total_sessions,
                        "average_score": await conn.fetchval("SELECT AVG(overall_score) FROM scorecards")
                    }
        except Exception:
            db_stats = {"error": "Unable to fetch database statistics"}
        
        return {
            "task_statistics": task_stats,
            "database_statistics": db_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    return router


# Utility functions for API responses
def create_error_response(message: str, status_code: int = 400) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def create_success_response(data: Dict, message: str = "Success") -> JSONResponse:
    """Create standardized success response."""
    return JSONResponse(
        content={
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    )