"""Integration tests for the post-interview analytics API.

This module tests the complete API endpoints with authentication,
authorization, and database integration.
"""

from __future__ import annotations

import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from fastapi import FastAPI

from post_interview.api import create_analytics_router
from post_interview.auth import RBACManager, UserRole
from post_interview.database import AnalyticsDatabase, AuditLogger
from post_interview.models import AnalyticsConfig, ScoreCard


@pytest.fixture
def mock_database():
    """Create mock database for testing."""
    db = AsyncMock(spec=AnalyticsDatabase)
    db.pool = AsyncMock()
    return db


@pytest.fixture
def rbac_manager():
    """Create RBAC manager for testing."""
    rbac = RBACManager("test_secret_key")
    rbac.create_default_users()
    return rbac


@pytest.fixture
def audit_logger(mock_database):
    """Create audit logger for testing."""
    return AuditLogger(mock_database)


@pytest.fixture
def mock_analytics_engine():
    """Create mock analytics engine."""
    engine = AsyncMock()
    return engine


@pytest.fixture
def mock_task_manager():
    """Create mock task manager."""
    task_manager = AsyncMock()
    task_manager.submit_task.return_value = "test_task_id"
    task_manager.get_task_status.return_value = None
    task_manager.get_user_tasks.return_value = []
    task_manager.cancel_task.return_value = True
    task_manager.get_task_statistics.return_value = {
        "total_tasks": 10,
        "completed_tasks": 8,
        "failed_tasks": 1,
        "success_rate": 80.0
    }
    return task_manager


@pytest.fixture
def app(mock_database, rbac_manager, audit_logger, mock_analytics_engine, mock_task_manager):
    """Create FastAPI app with analytics router."""
    app = FastAPI()
    router = create_analytics_router(
        database=mock_database,
        rbac_manager=rbac_manager,
        audit_logger=audit_logger,
        analytics_engine=mock_analytics_engine,
        task_manager=mock_task_manager
    )
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def admin_token(rbac_manager):
    """Get admin authentication token."""
    user = rbac_manager.authenticate_user("admin", "admin123")
    return rbac_manager.generate_token(user)


@pytest.fixture
def recruiter_token(rbac_manager):
    """Get recruiter authentication token."""
    user = rbac_manager.authenticate_user("recruiter", "rec123")
    return rbac_manager.generate_token(user)


@pytest.fixture
def interviewer_token(rbac_manager):
    """Get interviewer authentication token."""
    user = rbac_manager.authenticate_user("interviewer", "int123")
    return rbac_manager.generate_token(user)


@pytest.fixture
def viewer_token(rbac_manager):
    """Get viewer authentication token."""
    user = rbac_manager.authenticate_user("viewer", "view123")
    return rbac_manager.generate_token(user)


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_login_success(self, client):
        """Test successful login."""
        response = client.post(
            "/api/v1/analytics/auth/login",
            params={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/analytics/auth/login",
            params={"username": "admin", "password": "wrongpass"}
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    def test_logout_success(self, client, admin_token):
        """Test successful logout."""
        response = client.post(
            "/api/v1/analytics/auth/logout",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
    
    def test_logout_without_token(self, client):
        """Test logout without authentication token."""
        response = client.post("/api/v1/analytics/auth/logout")
        
        assert response.status_code == 401


class TestScorecardEndpoints:
    """Test scorecard endpoints."""
    
    def test_get_scorecard_admin(self, client, admin_token, mock_database):
        """Test get scorecard with admin permissions."""
        # Mock database response
        mock_scorecard = {
            "session_id": "session_123",
            "candidate_id": "candidate_456",
            "overall_score": 85.5,
            "job_match_percentage": 78.2
        }
        mock_database.get_scorecard.return_value = mock_scorecard
        
        response = client.get(
            "/api/v1/analytics/scorecards/session_123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "session_123"
        assert data["overall_score"] == 85.5
    
    def test_get_scorecard_recruiter(self, client, recruiter_token, mock_database):
        """Test get scorecard with recruiter permissions."""
        mock_scorecard = {
            "session_id": "session_123",
            "candidate_id": "candidate_456",
            "overall_score": 85.5
        }
        mock_database.get_scorecard.return_value = mock_scorecard
        
        response = client.get(
            "/api/v1/analytics/scorecards/session_123",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
    
    def test_get_scorecard_unauthorized(self, client, viewer_token):
        """Test get scorecard with viewer permissions (should fail)."""
        response = client.get(
            "/api/v1/analytics/scorecards/session_123",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_scorecard_not_found(self, client, admin_token, mock_database):
        """Test get scorecard that doesn't exist."""
        mock_database.get_scorecard.return_value = None
        
        response = client.get(
            "/api/v1/analytics/scorecards/nonexistent",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
        assert "Scorecard not found" in response.json()["detail"]
    
    def test_get_candidate_scorecards(self, client, recruiter_token, mock_database):
        """Test get all scorecards for a candidate."""
        mock_scorecards = [
            {"session_id": "session_1", "overall_score": 85.0},
            {"session_id": "session_2", "overall_score": 78.5}
        ]
        mock_database.get_candidate_scorecards.return_value = mock_scorecards
        
        response = client.get(
            "/api/v1/analytics/scorecards/candidate_456",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["scorecards"]) == 2
    
    def test_get_job_scorecards(self, client, recruiter_token, mock_database):
        """Test get all scorecards for a job."""
        mock_scorecards = [
            {"session_id": "session_1", "overall_score": 90.0},
            {"session_id": "session_2", "overall_score": 85.0},
            {"session_id": "session_3", "overall_score": 80.0}
        ]
        mock_database.get_job_scorecards.return_value = mock_scorecards
        
        response = client.get(
            "/api/v1/analytics/scorecards/job_789?limit=2&offset=0",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["scorecards"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    def test_regenerate_scorecard(self, client, admin_token, mock_task_manager):
        """Test scorecard regeneration."""
        response = client.post(
            "/api/v1/analytics/scorecards/session_123/regenerate",
            json=["Python", "Django", "API Development"],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["message"] == "Scorecard regeneration started"
        mock_task_manager.submit_task.assert_called_once()


class TestExportEndpoints:
    """Test export endpoints."""
    
    def test_export_scorecard_json(self, client, recruiter_token, mock_task_manager):
        """Test scorecard export in JSON format."""
        response = client.post(
            "/api/v1/analytics/export/scorecards/session_123?export_format=json",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "json" in data["message"]
    
    def test_export_scorecard_pdf(self, client, recruiter_token, mock_task_manager):
        """Test scorecard export in PDF format."""
        response = client.post(
            "/api/v1/analytics/export/scorecards/session_123?export_format=pdf",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "pdf" in data["message"]
    
    def test_export_unauthorized(self, client, viewer_token):
        """Test export with insufficient permissions."""
        response = client.post(
            "/api/v1/analytics/export/scorecards/session_123",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403


class TestTaskEndpoints:
    """Test task management endpoints."""
    
    def test_get_task_status(self, client, admin_token, mock_task_manager):
        """Test get task status."""
        mock_task = {
            "task_id": "task_123",
            "status": "completed",
            "result": {"processed": True}
        }
        mock_task_manager.get_task_status.return_value = mock_task
        
        response = client.get(
            "/api/v1/analytics/tasks/task_123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task_123"
        assert data["status"] == "completed"
    
    def test_get_session_tasks(self, client, interviewer_token, mock_task_manager):
        """Test get tasks for a session."""
        mock_tasks = [
            {"task_id": "task_1", "status": "completed"},
            {"task_id": "task_2", "status": "running"}
        ]
        mock_task_manager.get_user_tasks.return_value = mock_tasks
        
        response = client.get(
            "/api/v1/analytics/tasks/session/session_123",
            headers={"Authorization": f"Bearer {interviewer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 2
    
    def test_cancel_task(self, client, admin_token, mock_task_manager):
        """Test task cancellation."""
        response = client.post(
            "/api/v1/analytics/tasks/task_123/cancel",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Task cancelled successfully"
        mock_task_manager.cancel_task.assert_called_once_with("task_123")


class TestConfigurationEndpoints:
    """Test configuration endpoints."""
    
    def test_get_analytics_config(self, client, recruiter_token):
        """Test get analytics configuration."""
        response = client.get(
            "/api/v1/analytics/config",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "skill_weight" in data
        assert "clarity_weight" in data
        assert "competency_weight" in data
    
    def test_update_analytics_config_admin(self, client, admin_token):
        """Test update analytics configuration as admin."""
        new_config = {
            "skill_weight": 0.5,
            "clarity_weight": 0.25,
            "competency_weight": 0.25
        }
        
        response = client.put(
            "/api/v1/analytics/config",
            json=new_config,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "Configuration updated successfully" in response.json()["message"]
    
    def test_update_analytics_config_unauthorized(self, client, recruiter_token):
        """Test update analytics configuration as non-admin."""
        new_config = {
            "skill_weight": 0.5,
            "clarity_weight": 0.25,
            "competency_weight": 0.25
        }
        
        response = client.put(
            "/api/v1/analytics/config",
            json=new_config,
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 403


class TestAuditEndpoints:
    """Test audit endpoints."""
    
    def test_get_audit_trail_admin(self, client, admin_token, audit_logger):
        """Test get audit trail as admin."""
        # Mock audit logger response
        mock_entries = [
            {
                "log_id": "audit_1",
                "user_id": "admin",
                "action": "ACCESS",
                "resource_type": "scorecards",
                "resource_id": "session_123",
                "timestamp": datetime.utcnow()
            }
        ]
        
        with patch.object(audit_logger, 'get_audit_trail', return_value=mock_entries):
            response = client.get(
                "/api/v1/analytics/audit/scorecards/session_123",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["audit_trail"]) == 1
        assert data["resource_type"] == "scorecards"
        assert data["resource_id"] == "session_123"
    
    def test_get_audit_trail_unauthorized(self, client, recruiter_token):
        """Test get audit trail without sufficient permissions."""
        response = client.get(
            "/api/v1/analytics/audit/scorecards/session_123",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 403


class TestStatisticsEndpoints:
    """Test statistics endpoints."""
    
    def test_get_analytics_statistics(self, client, recruiter_token, mock_task_manager, mock_database):
        """Test get analytics statistics."""
        # Mock database statistics
        mock_database.pool.__aenter__.return_value.fetchval.side_effect = [5, 3, 82.5]
        
        response = client.get(
            "/api/v1/analytics/statistics",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_statistics" in data
        assert "database_statistics" in data
        assert "generated_at" in data
        
        # Check task statistics
        task_stats = data["task_statistics"]
        assert "total_tasks" in task_stats
        assert "success_rate" in task_stats
        
        # Check database statistics
        db_stats = data["database_statistics"]
        assert "total_scorecards" in db_stats
        assert "total_sessions" in db_stats


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_token(self, client):
        """Test API with invalid token."""
        response = client.get(
            "/api/v1/analytics/scorecards/session_123",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_missing_token(self, client):
        """Test API without token."""
        response = client.get("/api/v1/analytics/scorecards/session_123")
        
        assert response.status_code == 401
    
    def test_invalid_export_format(self, client, recruiter_token):
        """Test export with invalid format."""
        response = client.post(
            "/api/v1/analytics/export/scorecards/session_123?export_format=xml",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_pagination_limits(self, client, recruiter_token):
        """Test pagination parameter validation."""
        # Test limit over maximum
        response = client.get(
            "/api/v1/analytics/scorecards/job_789?limit=200",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test negative offset
        response = client.get(
            "/api/v1/analytics/scorecards/job_789?offset=-1",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        
        assert response.status_code == 422  # Validation error


class TestAPIIntegration:
    """Integration tests for API workflows."""
    
    def test_complete_analytics_workflow(self, client, admin_token, mock_database, mock_task_manager):
        """Test complete analytics workflow."""
        # Setup mocks
        mock_scorecard = {
            "session_id": "session_123",
            "candidate_id": "candidate_456",
            "overall_score": 85.5,
            "job_match_percentage": 78.2,
            "feedback_narrative": "Strong technical skills demonstrated."
        }
        mock_database.get_scorecard.return_value = mock_scorecard
        
        # Step 1: Get scorecard
        response = client.get(
            "/api/v1/analytics/scorecards/session_123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Step 2: Regenerate scorecard
        response = client.post(
            "/api/v1/analytics/scorecards/session_123/regenerate",
            json=["Python", "Django"],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Step 3: Check task status
        task_id = response.json()["task_id"]
        mock_task = {
            "task_id": task_id,
            "status": "completed",
            "result": {"processed": True}
        }
        mock_task_manager.get_task_status.return_value = mock_task
        
        response = client.get(
            f"/api/v1/analytics/tasks/{task_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Step 4: Export scorecard
        response = client.post(
            "/api/v1/analytics/export/scorecards/session_123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Step 5: Get statistics
        mock_database.pool.__aenter__.return_value.fetchval.side_effect = [5, 3, 82.5]
        response = client.get(
            "/api/v1/analytics/statistics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])