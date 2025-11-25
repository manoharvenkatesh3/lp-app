from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import candidates

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
