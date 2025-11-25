"""Background task orchestration for post-interview analytics.

This module provides asynchronous task processing with retries,
observability, and error handling for interview analytics.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from .models import BackgroundTask, TaskStatus
from .database import AnalyticsDatabase


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskResult:
    """Result of a background task execution."""
    
    def __init__(self, success: bool, data: Optional[Dict] = None,
                 error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()


class BackgroundTaskManager:
    """Manages background task execution with retry logic and observability."""
    
    def __init__(self, database: AnalyticsDatabase, max_concurrent_tasks: int = 5):
        self.database = database
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.task_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retried_tasks": 0
        }
    
    async def start(self) -> None:
        """Start the background task manager."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start worker coroutines
        for i in range(self.max_concurrent_tasks):
            asyncio.create_task(self._worker(f"worker-{i}"))
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_completed_tasks())
    
    async def stop(self) -> None:
        """Stop the background task manager."""
        self.is_running = False
        
        # Wait for running tasks to complete
        for task_id, task in self.running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def register_task_handler(self, task_type: str, handler: Callable) -> None:
        """Register a handler for a specific task type."""
        self.task_handlers[task_type] = handler
    
    async def submit_task(self, task_type: str, session_id: str,
                         task_data: Optional[Dict] = None,
                         priority: TaskPriority = TaskPriority.NORMAL,
                         max_retries: int = 3) -> str:
        """Submit a task for background processing."""
        task_id = str(uuid.uuid4())
        
        # Create task record
        background_task = BackgroundTask(
            task_id=task_id,
            session_id=session_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            max_retries=max_retries
        )
        
        # Store task in database
        await self._store_task(background_task)
        
        # Add to queue with priority
        await self.task_queue.put((priority.value, task_id, task_data or {}))
        
        self.task_stats["total_tasks"] += 1
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[BackgroundTask]:
        """Get status of a specific task."""
        if not self.database.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.database.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM background_tasks WHERE task_id = $1
            """, task_id)
            
            if row:
                return BackgroundTask(**dict(row))
            return None
    
    async def get_user_tasks(self, session_id: str) -> List[BackgroundTask]:
        """Get all tasks for a specific session."""
        if not self.database.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.database.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM background_tasks 
                WHERE session_id = $1 
                ORDER BY created_at DESC
            """, session_id)
            
            return [BackgroundTask(**dict(row)) for row in rows]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            
            # Update database
            await self._update_task_status(task_id, TaskStatus.FAILED, "Task cancelled")
            
            return True
        return False
    
    async def _worker(self, worker_name: str) -> None:
        """Worker coroutine that processes tasks from the queue."""
        while self.is_running:
            try:
                # Get task from queue (with timeout)
                priority, task_id, task_data = await asyncio.wait_for(
                    self.task_queue.get(), timeout=1.0
                )
                
                # Process the task
                await self._process_task(task_id, task_data, worker_name)
                
            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                print(f"Worker {worker_name} error: {e}")
                continue
    
    async def _process_task(self, task_id: str, task_data: Dict, worker_name: str) -> None:
        """Process a single task."""
        try:
            # Get task from database
            task = await self.get_task_status(task_id)
            if not task:
                return
            
            # Update status to running
            await self._update_task_status(task_id, TaskStatus.RUNNING, started_at=datetime.utcnow())
            
            # Get task handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task.task_type}")
            
            # Create asyncio task
            async_task = asyncio.create_task(
                self._execute_task_handler(task_id, handler, task_data, worker_name)
            )
            self.running_tasks[task_id] = async_task
            
            # Wait for completion
            try:
                result = await async_task
                await self._handle_task_completion(task_id, result)
            finally:
                self.running_tasks.pop(task_id, None)
                
        except Exception as e:
            await self._handle_task_error(task_id, str(e))
    
    async def _execute_task_handler(self, task_id: str, handler: Callable,
                                   task_data: Dict, worker_name: str) -> TaskResult:
        """Execute the task handler and return result."""
        try:
            # Call the handler
            result_data = await handler(task_id, task_data)
            
            return TaskResult(
                success=True,
                data=result_data,
                error=None
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _handle_task_completion(self, task_id: str, result: TaskResult) -> None:
        """Handle successful task completion."""
        if result.success:
            await self._update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result.data
            )
            self.task_stats["completed_tasks"] += 1
        else:
            await self._handle_task_error(task_id, result.error)
    
    async def _handle_task_error(self, task_id: str, error_message: str) -> None:
        """Handle task error and retry logic."""
        task = await self.get_task_status(task_id)
        if not task:
            return
        
        if task.retry_count < task.max_retries:
            # Retry the task
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            
            await self._update_task_status(
                task_id,
                TaskStatus.RETRYING,
                error_message=error_message,
                retry_count=task.retry_count
            )
            
            # Add exponential backoff delay
            delay = min(300, (2 ** task.retry_count))  # Max 5 minutes
            await asyncio.sleep(delay)
            
            # Re-queue the task
            await self.task_queue.put((TaskPriority.NORMAL.value, task_id, {}))
            self.task_stats["retried_tasks"] += 1
            
        else:
            # Mark as failed
            await self._update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=error_message,
                completed_at=datetime.utcnow()
            )
            self.task_stats["failed_tasks"] += 1
    
    async def _store_task(self, task: BackgroundTask) -> None:
        """Store task in database."""
        if not self.database.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.database.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO background_tasks 
                (task_id, session_id, task_type, status, created_at, 
                 started_at, completed_at, error_message, retry_count, max_retries, result)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """, task.task_id, task.session_id, task.task_type, task.status,
                 task.created_at, task.started_at, task.completed_at,
                 task.error_message, task.retry_count, task.max_retries,
                 task.result)
    
    async def _update_task_status(self, task_id: str, status: TaskStatus,
                                error_message: Optional[str] = None,
                                started_at: Optional[datetime] = None,
                                completed_at: Optional[datetime] = None,
                                result: Optional[Dict] = None,
                                retry_count: Optional[int] = None) -> None:
        """Update task status in database."""
        if not self.database.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.database.pool.acquire() as conn:
            await conn.execute("""
                UPDATE background_tasks 
                SET status = $1, 
                    error_message = COALESCE($2, error_message),
                    started_at = COALESCE($3, started_at),
                    completed_at = COALESCE($4, completed_at),
                    result = COALESCE($5, result),
                    retry_count = COALESCE($6, retry_count)
                WHERE task_id = $7
            """, status.value, error_message, started_at, completed_at,
                 result, retry_count, task_id)
    
    async def _cleanup_completed_tasks(self) -> None:
        """Cleanup old completed tasks periodically."""
        while self.is_running:
            try:
                # Clean up tasks older than 7 days
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                if self.database.pool:
                    async with self.database.pool.acquire() as conn:
                        await conn.execute("""
                            DELETE FROM background_tasks 
                            WHERE status IN ('completed', 'failed') 
                            AND completed_at < $1
                        """, cutoff_date)
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                print(f"Cleanup task error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    def get_task_statistics(self) -> Dict:
        """Get task processing statistics."""
        return {
            **self.task_stats,
            "active_tasks": len(self.running_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "success_rate": (
                self.task_stats["completed_tasks"] / max(1, self.task_stats["total_tasks"]) * 100
            )
        }


class InterviewAnalyticsTaskHandler:
    """Task handler for interview analytics processing."""
    
    def __init__(self, analytics_engine, database: AnalyticsDatabase):
        self.analytics_engine = analytics_engine
        self.database = database
    
    async def process_interview_analytics(self, task_id: str, task_data: Dict) -> Dict:
        """Process interview analytics for a session."""
        session_id = task_data.get("session_id")
        job_requirements = task_data.get("job_requirements", [])
        
        if not session_id:
            raise ValueError("Session ID is required")
        
        # Get transcript data from database
        transcript_data = await self._get_transcript_data(session_id)
        if not transcript_data:
            raise ValueError(f"No transcript found for session: {session_id}")
        
        # Process analytics
        scorecard = self.analytics_engine.analyze_interview(transcript_data, job_requirements)
        
        # Store scorecard
        await self.database.store_scorecard(scorecard)
        
        return {
            "session_id": session_id,
            "scorecard_id": f"sc_{session_id}",
            "overall_score": scorecard.overall_score,
            "job_match_percentage": scorecard.job_match_percentage,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _get_transcript_data(self, session_id: str):
        """Get transcript data from database."""
        if not self.database.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.database.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM transcript_data WHERE session_id = $1
            """, session_id)
            
            if row:
                from .models import TranscriptData
                return TranscriptData(**dict(row))
            return None


# Default task handlers that can be registered
async def analytics_task_handler(task_id: str, task_data: Dict) -> Dict:
    """Default analytics task handler."""
    # This would be replaced with actual analytics processing
    await asyncio.sleep(2)  # Simulate processing time
    
    session_id = task_data.get("session_id", "unknown")
    
    return {
        "session_id": session_id,
        "status": "processed",
        "processed_at": datetime.utcnow().isoformat()
    }


async def export_task_handler(task_id: str, task_data: Dict) -> Dict:
    """Default export task handler."""
    # This would handle PDF/JSON exports
    await asyncio.sleep(1)  # Simulate processing time
    
    export_type = task_data.get("export_type", "json")
    resource_id = task_data.get("resource_id", "unknown")
    
    return {
        "export_type": export_type,
        "resource_id": resource_id,
        "export_url": f"/exports/{resource_id}.{export_type}",
        "exported_at": datetime.utcnow().isoformat()
    }