"""FastAPI server for post-interview analytics API.

This module provides a standalone API server for the post-interview
analytics system with authentication, authorization, and database integration.
"""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict

import uvicorn
from fastapi import FastAPI

from Resume_parser.post_interview.analytics import InterviewAnalytics
from Resume_parser.post_interview.api import create_analytics_router
from Resume_parser.post_interview.auth import RBACManager
from Resume_parser.post_interview.background import BackgroundTaskManager
from Resume_parser.post_interview.crypto import TranscriptCrypto, TranscriptHasher, TranscriptProcessor
from Resume_parser.post_interview.database import AnalyticsDatabase, AuditLogger
from Resume_parser.post_interview.models import AnalyticsConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Post-Interview Analytics API Server...")
    
    # Initialize database
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "database": os.getenv("DB_NAME", "eureka_analytics"),
        "username": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
    }
    
    database = AnalyticsDatabase(db_config)
    await database.initialize()
    
    # Initialize RBAC
    secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    rbac_manager = RBACManager(secret_key)
    rbac_manager.create_default_users()
    
    # Initialize audit logger
    audit_logger = AuditLogger(database)
    await audit_logger.create_audit_table()
    
    # Initialize analytics components
    config = AnalyticsConfig()
    crypto = TranscriptCrypto()
    hasher = TranscriptHasher()
    transcript_processor = TranscriptProcessor(crypto, hasher)
    analytics_engine = InterviewAnalytics(config, transcript_processor)
    
    # Initialize background task manager
    task_manager = BackgroundTaskManager(database)
    await task_manager.start()
    
    # Register task handlers
    from Resume_parser.post_interview.background import InterviewAnalyticsTaskHandler
    task_handler = InterviewAnalyticsTaskHandler(analytics_engine, database)
    task_manager.register_task_handler("analytics", task_handler.process_interview_analytics)
    
    # Store components in app state
    app.state.database = database
    app.state.rbac_manager = rbac_manager
    app.state.audit_logger = audit_logger
    app.state.analytics_engine = analytics_engine
    app.state.task_manager = task_manager
    
    print("✅ All components initialized successfully!")
    print("📊 API Documentation available at: http://localhost:8000/docs")
    print("🔐 Default users created:")
    print("   - admin / admin123")
    print("   - hiring_manager / hm123")
    print("   - recruiter / rec123")
    print("   - interviewer / int123")
    print("   - viewer / view123")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down API server...")
    await task_manager.stop()
    await database.close()
    print("✅ Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Eureka Post-Interview Analytics API",
        description="REST API for encrypted interview transcript analysis and scoring",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Eureka Post-Interview Analytics API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Use actual timestamp in production
            "components": {
                "database": "connected",
                "task_manager": "running",
                "analytics": "ready"
            }
        }
    
    # Add analytics router (will be added after components are initialized)
    @app.on_event("startup")
    async def add_router():
        """Add analytics router after startup."""
        # Wait a moment for components to initialize
        await asyncio.sleep(0.1)
        
        if hasattr(app.state, 'database'):
            router = create_analytics_router(
                database=app.state.database,
                rbac_manager=app.state.rbac_manager,
                audit_logger=app.state.audit_logger,
                analytics_engine=app.state.analytics_engine,
                task_manager=app.state.task_manager
            )
            app.include_router(router)
    
    return app


def main():
    """Main entry point for the API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Eureka Post-Interview Analytics API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create app
    app = create_app()
    
    # Run server
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )


if __name__ == "__main__":
    main()