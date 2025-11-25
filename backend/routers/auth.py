"""Authentication routes."""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..middleware.audit import log_action
from ..middleware.rbac import get_current_active_user
from ..models import User
from ..schemas.auth import Token, UserCreate, UserLogin, UserResponse
from ..utils.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role,
    )
    
    db.add(user)
    await db.flush()
    
    # Log action
    await log_action(
        db=db,
        user=user,
        action="user_registered",
        resource_type="user",
        resource_id=user.id,
    )
    
    await db.commit()
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and receive JWT tokens."""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )
    
    # Create tokens
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.value,
    }
    
    access_token = create_access_token(
        token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(token_data)
    
    # Log action
    await log_action(
        db=db,
        user=user,
        action="user_login",
        resource_type="user",
        resource_id=user.id,
    )
    
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user information."""
    return current_user


@router.get("/role")
async def detect_role(current_user: User = Depends(get_current_active_user)):
    """Detect current user's role for frontend routing."""
    return {
        "role": current_user.role.value,
        "permissions": _get_role_permissions(current_user.role.value),
    }


def _get_role_permissions(role: str) -> list[str]:
    """Get permissions for a role."""
    permissions_map = {
        "admin": [
            "manage_users",
            "view_all_interviews",
            "manage_ats",
            "view_audit_logs",
            "manage_scorecards",
            "schedule_interviews",
        ],
        "hiring_manager": [
            "view_team_interviews",
            "manage_scorecards",
            "schedule_interviews",
            "view_analytics",
        ],
        "recruiter": [
            "view_own_interviews",
            "create_scorecards",
            "schedule_interviews",
            "monitor_interviews",
        ],
    }
    return permissions_map.get(role, [])
