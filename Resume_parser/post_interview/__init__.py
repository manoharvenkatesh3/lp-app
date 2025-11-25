"""Post-interview analytics module for Eureka AI Talent Discovery Engine.

This module provides comprehensive post-interview analysis including:
- Encrypted transcript processing
- Strengths/weakness extraction
- Bias-free scoring (skill, clarity, competency axes)
- Job match percentage calculation
- Auto-feedback narratives with transparent scoring
- PostgreSQL persistence with audit logging
- REST API endpoints with RBAC protection
- Background task orchestration
"""

from __future__ import annotations

from .analytics import (
    InterviewAnalytics,
    PostInterviewProcessor,
    ScoreCard,
    TranscriptAnalyzer,
)
from .api import create_analytics_router
from .auth import RBACManager, UserRole
from .background import BackgroundTaskManager, TaskStatus
from .crypto import TranscriptCrypto, TranscriptHasher, TranscriptProcessor
from .database import AnalyticsDatabase, AuditLogger
from .models import (
    AnalyticsConfig,
    InterviewSession,
    ScoringAxes,
    StrengthWeakness,
    TranscriptData,
)

__all__ = [
    "InterviewAnalytics",
    "PostInterviewProcessor", 
    "ScoreCard",
    "TranscriptAnalyzer",
    "create_analytics_router",
    "RBACManager",
    "UserRole",
    "BackgroundTaskManager",
    "TaskStatus",
    "TranscriptCrypto",
    "TranscriptHasher",
    "TranscriptProcessor",
    "AnalyticsDatabase",
    "AuditLogger",
    "AnalyticsConfig",
    "InterviewSession",
    "ScoringAxes",
    "StrengthWeakness",
    "TranscriptData",
]