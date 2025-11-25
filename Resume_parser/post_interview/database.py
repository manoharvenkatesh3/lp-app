"""PostgreSQL database integration for analytics and audit logging.

This module provides secure database operations for storing interview
analytics, scorecards, and comprehensive audit trails.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import asyncpg
from pydantic import BaseModel

from .models import (
    AnalyticsConfig,
    AuditLogEntry,
    BackgroundTask,
    InterviewSession,
    ScoreCard,
    TaskStatus,
    TranscriptData,
    UserRole,
)


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "eureka_analytics"
    username: str
    password: str
    min_size: int = 5
    max_size: int = 20


class AnalyticsDatabase:
    """Database manager for interview analytics."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self) -> None:
        """Initialize database connection pool and create tables."""
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.username,
            password=self.config.password,
            min_size=self.config.min_size,
            max_size=self.config.max_size,
        )
        
        await self._create_tables()
        await self._create_indexes()
    
    async def _create_tables(self) -> None:
        """Create database tables."""
        async with self.pool.acquire() as conn:
            # Interview sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS interview_sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    candidate_id VARCHAR(255) NOT NULL,
                    candidate_name VARCHAR(255) NOT NULL,
                    job_id VARCHAR(255) NOT NULL,
                    job_title VARCHAR(255) NOT NULL,
                    interviewer_id VARCHAR(255) NOT NULL,
                    interviewer_name VARCHAR(255) NOT NULL,
                    interview_date TIMESTAMP NOT NULL,
                    interview_type VARCHAR(100) NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    status VARCHAR(50) DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transcript data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transcript_data (
                    session_id VARCHAR(255) PRIMARY KEY,
                    candidate_id VARCHAR(255) NOT NULL,
                    job_id VARCHAR(255) NOT NULL,
                    interview_type VARCHAR(100) NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    encrypted_content TEXT NOT NULL,
                    content_hash VARCHAR(64) NOT NULL,
                    signature VARCHAR(128),
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Scorecards table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS scorecards (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    candidate_id VARCHAR(255) NOT NULL,
                    job_id VARCHAR(255) NOT NULL,
                    skill_score FLOAT CHECK (skill_score >= 0 AND skill_score <= 100),
                    clarity_score FLOAT CHECK (clarity_score >= 0 AND clarity_score <= 100),
                    competency_score FLOAT CHECK (competency_score >= 0 AND competency_score <= 100),
                    overall_score FLOAT CHECK (overall_score >= 0 AND overall_score <= 100),
                    job_match_percentage FLOAT CHECK (job_match_percentage >= 0 AND job_match_percentage <= 100),
                    strengths TEXT[],
                    weaknesses TEXT[],
                    evidence JSONB,
                    feedback_narrative TEXT,
                    scoring_methodology JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Background tasks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS background_tasks (
                    task_id VARCHAR(255) PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    task_type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    result JSONB,
                    FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id) ON DELETE CASCADE
                )
            """)
            
            # Analytics config table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_config (
                    id SERIAL PRIMARY KEY,
                    skill_weight FLOAT DEFAULT 0.4 CHECK (skill_weight >= 0 AND skill_weight <= 1),
                    clarity_weight FLOAT DEFAULT 0.3 CHECK (clarity_weight >= 0 AND clarity_weight <= 1),
                    competency_weight FLOAT DEFAULT 0.3 CHECK (competency_weight >= 0 AND competency_weight <= 1),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT weights_sum CHECK (skill_weight + clarity_weight + competency_weight = 1.0)
                )
            """)
    
    async def _create_indexes(self) -> None:
        """Create database indexes for performance."""
        async with self.pool.acquire() as conn:
            # Session indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_candidate ON interview_sessions(candidate_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_job ON interview_sessions(job_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON interview_sessions(interview_date)")
            
            # Scorecard indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_scorecards_candidate ON scorecards(candidate_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_scorecards_job ON scorecards(job_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_scorecards_overall ON scorecards(overall_score)")
            
            # Task indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON background_tasks(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_session ON background_tasks(session_id)")
    
    async def store_interview_session(self, session: InterviewSession) -> None:
        """Store interview session data."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO interview_sessions 
                (session_id, candidate_id, candidate_name, job_id, job_title,
                 interviewer_id, interviewer_name, interview_date, interview_type,
                 duration_minutes, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (session_id) DO UPDATE SET
                    candidate_name = EXCLUDED.candidate_name,
                    job_title = EXCLUDED.job_title,
                    interviewer_name = EXCLUDED.interviewer_name,
                    interview_date = EXCLUDED.interview_date,
                    interview_type = EXCLUDED.interview_type,
                    duration_minutes = EXCLUDED.duration_minutes,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """, session.session_id, session.candidate_id, session.candidate_name,
                 session.job_id, session.job_title, session.interviewer_id,
                 session.interviewer_name, session.interview_date,
                 session.interview_type, session.duration_minutes, session.status)
    
    async def store_transcript(self, transcript: TranscriptData) -> None:
        """Store encrypted transcript data."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO transcript_data 
                (session_id, candidate_id, job_id, interview_type, duration_minutes,
                 encrypted_content, content_hash, signature, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (session_id) DO UPDATE SET
                    encrypted_content = EXCLUDED.encrypted_content,
                    content_hash = EXCLUDED.content_hash,
                    signature = EXCLUDED.signature,
                    timestamp = EXCLUDED.timestamp
            """, transcript.session_id, transcript.candidate_id, transcript.job_id,
                 transcript.interview_type, transcript.duration_minutes,
                 transcript.encrypted_content, transcript.content_hash,
                 transcript.signature, transcript.timestamp)
    
    async def store_scorecard(self, scorecard: ScoreCard) -> None:
        """Store scorecard data."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO scorecards 
                (session_id, candidate_id, job_id, skill_score, clarity_score,
                 competency_score, overall_score, job_match_percentage,
                 strengths, weaknesses, evidence, feedback_narrative, scoring_methodology)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (session_id) DO UPDATE SET
                    skill_score = EXCLUDED.skill_score,
                    clarity_score = EXCLUDED.clarity_score,
                    competency_score = EXCLUDED.competency_score,
                    overall_score = EXCLUDED.overall_score,
                    job_match_percentage = EXCLUDED.job_match_percentage,
                    strengths = EXCLUDED.strengths,
                    weaknesses = EXCLUDED.weaknesses,
                    evidence = EXCLUDED.evidence,
                    feedback_narrative = EXCLUDED.feedback_narrative,
                    scoring_methodology = EXCLUDED.scoring_methodology,
                    updated_at = CURRENT_TIMESTAMP
            """, scorecard.session_id, scorecard.candidate_id, scorecard.job_id,
                 scorecard.scoring_axes.skill_score, scorecard.scoring_axes.clarity_score,
                 scorecard.scoring_axes.competency_score, scorecard.overall_score,
                 scorecard.job_match_percentage, scorecard.strengths_weaknesses.strengths,
                 scorecard.strengths_weaknesses.weaknesses,
                 json.dumps(scorecard.strengths_weaknesses.evidence),
                 scorecard.feedback_narrative, json.dumps(scorecard.scoring_methodology))
    
    async def get_scorecard(self, session_id: str) -> Optional[Dict]:
        """Retrieve scorecard by session ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM scorecards WHERE session_id = $1
            """, session_id)
            
            if row:
                return dict(row)
            return None
    
    async def get_candidate_scorecards(self, candidate_id: str) -> List[Dict]:
        """Get all scorecards for a candidate."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM scorecards WHERE candidate_id = $1 ORDER BY created_at DESC
            """, candidate_id)
            return [dict(row) for row in rows]
    
    async def get_job_scorecards(self, job_id: str) -> List[Dict]:
        """Get all scorecards for a job position."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM scorecards WHERE job_id = $1 ORDER BY overall_score DESC
            """, job_id)
            return [dict(row) for row in rows]
    
    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()


class AuditLogger:
    """Audit logging for compliance and security monitoring."""
    
    def __init__(self, db: AnalyticsDatabase):
        self.db = db
    
    async def log_access(self, user_id: str, user_role: UserRole, 
                        resource_type: str, resource_id: str,
                        session_id: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> None:
        """Log resource access."""
        await self._log_entry(
            user_id=user_id,
            user_role=user_role,
            action="ACCESS",
            resource_type=resource_type,
            resource_id=resource_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_update(self, user_id: str, user_role: UserRole,
                        resource_type: str, resource_id: str,
                        changes_made: Dict,
                        session_id: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> None:
        """Log resource update."""
        await self._log_entry(
            user_id=user_id,
            user_role=user_role,
            action="UPDATE",
            resource_type=resource_type,
            resource_id=resource_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes_made=changes_made
        )
    
    async def log_delete(self, user_id: str, user_role: UserRole,
                        resource_type: str, resource_id: str,
                        session_id: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> None:
        """Log resource deletion."""
        await self._log_entry(
            user_id=user_id,
            user_role=user_role,
            action="DELETE",
            resource_type=resource_type,
            resource_id=resource_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def _log_entry(self, user_id: str, user_role: UserRole,
                        action: str, resource_type: str, resource_id: str,
                        session_id: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None,
                        changes_made: Optional[Dict] = None) -> None:
        """Create audit log entry."""
        if not self.db.pool:
            raise RuntimeError("Database not initialized")
        
        # Generate unique log ID
        log_id = f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(resource_id)}"
        
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO audit_log 
                (log_id, session_id, user_id, user_role, action, resource_type, 
                 resource_id, ip_address, user_agent, changes_made)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, log_id, session_id, user_id, user_role.value, action,
                 resource_type, resource_id, ip_address, user_agent,
                 json.dumps(changes_made) if changes_made else None)
    
    async def create_audit_table(self) -> None:
        """Create audit log table if it doesn't exist."""
        if not self.db.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id VARCHAR(255) PRIMARY KEY,
                    session_id VARCHAR(255),
                    user_id VARCHAR(255) NOT NULL,
                    user_role VARCHAR(50) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    resource_type VARCHAR(100) NOT NULL,
                    resource_id VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT,
                    changes_made JSONB
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log(resource_type, resource_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
    
    async def get_audit_trail(self, resource_type: str, resource_id: str,
                             limit: int = 100) -> List[Dict]:
        """Get audit trail for a specific resource."""
        if not self.db.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM audit_log 
                WHERE resource_type = $1 AND resource_id = $2 
                ORDER BY timestamp DESC LIMIT $3
            """, resource_type, resource_id, limit)
            return [dict(row) for row in rows]