"""Role-based access control (RBAC) for analytics API.

This module provides authentication and authorization functionality
to ensure secure access to interview analytics data.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import jwt
from passlib.context import CryptContext

from .models import UserRole


class User:
    """User model for authentication and authorization."""
    
    def __init__(self, user_id: str, username: str, email: str,
                 role: UserRole, is_active: bool = True):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.last_login = None
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary representation."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class RBACManager:
    """Role-based access control manager."""
    
    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Role permissions matrix
        self.role_permissions = {
            UserRole.ADMIN: {
                "read": ["all"],
                "write": ["all"],
                "delete": ["all"],
                "export": ["all"],
                "manage_users": True,
                "view_audit": True
            },
            UserRole.HIRING_MANAGER: {
                "read": ["scorecards", "sessions", "analytics"],
                "write": ["scorecards", "feedback"],
                "delete": [],
                "export": ["scorecards", "analytics"],
                "manage_users": False,
                "view_audit": False
            },
            UserRole.RECRUITER: {
                "read": ["scorecards", "sessions"],
                "write": ["scorecards"],
                "delete": [],
                "export": ["scorecards"],
                "manage_users": False,
                "view_audit": False
            },
            UserRole.INTERVIEWER: {
                "read": ["own_sessions", "own_scorecards"],
                "write": ["own_scorecards"],
                "delete": [],
                "export": ["own_scorecards"],
                "manage_users": False,
                "view_audit": False
            },
            UserRole.VIEWER: {
                "read": ["assigned_scorecards", "assigned_sessions"],
                "write": [],
                "delete": [],
                "export": [],
                "manage_users": False,
                "view_audit": False
            }
        }
        
        # In-memory user store (in production, use database)
        self.users: Dict[str, User] = {}
        self.user_sessions: Dict[str, Dict] = {}
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, email: str, password: str,
                   role: UserRole) -> User:
        """Create new user."""
        user_id = f"user_{secrets.token_hex(8)}"
        hashed_password = self.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role
        )
        
        # Store user with hashed password
        self.users[user_id] = user
        self.user_sessions[user_id] = {
            "password_hash": hashed_password,
            "failed_attempts": 0,
            "locked_until": None
        }
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user and return user object if successful."""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # Check if account is locked
        session_data = self.user_sessions.get(user.user_id, {})
        if session_data.get("locked_until"):
            if datetime.utcnow() < session_data["locked_until"]:
                return None
            else:
                # Unlock account
                session_data["locked_until"] = None
                session_data["failed_attempts"] = 0
        
        # Verify password
        if not self.verify_password(password, session_data["password_hash"]):
            # Increment failed attempts
            session_data["failed_attempts"] += 1
            
            # Lock account after 5 failed attempts for 30 minutes
            if session_data["failed_attempts"] >= 5:
                session_data["locked_until"] = datetime.utcnow() + timedelta(minutes=30)
            
            return None
        
        # Reset failed attempts on successful login
        session_data["failed_attempts"] = 0
        user.last_login = datetime.utcnow()
        
        return user
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for authenticated user."""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user object from JWT token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        return self.users.get(user_id)
    
    def has_permission(self, user: User, action: str, resource: str,
                      resource_owner_id: Optional[str] = None) -> bool:
        """Check if user has permission for action on resource."""
        role_permissions = self.role_permissions.get(user.role, {})
        
        # Check admin privileges
        if role_permissions.get(action) == ["all"]:
            return True
        
        # Check specific resource permissions
        allowed_resources = role_permissions.get(action, [])
        
        # Check for "own_" prefixed resources
        if resource.startswith("own_") and resource_owner_id:
            if resource_owner_id == user.user_id:
                base_resource = resource.replace("own_", "")
                return base_resource in allowed_resources
        
        # Check direct resource access
        return resource in allowed_resources
    
    def check_resource_access(self, user: User, resource_type: str,
                            resource_id: str, action: str,
                            resource_owner_id: Optional[str] = None) -> bool:
        """Check if user can access specific resource."""
        # First check basic permission
        if not self.has_permission(user, action, resource_type, resource_owner_id):
            return False
        
        # Additional checks for specific resource types
        if resource_type == "scorecards":
            return self._check_scorecard_access(user, resource_id, action)
        elif resource_type == "sessions":
            return self._check_session_access(user, resource_id, action)
        
        return True
    
    def _check_scorecard_access(self, user: User, scorecard_id: str,
                               action: str) -> bool:
        """Check access to specific scorecard."""
        # In production, this would query the database
        # For now, we'll implement basic logic
        
        # Admins can access all
        if user.role == UserRole.ADMIN:
            return True
        
        # Hiring managers and recruiters can access all scorecards for read
        if action == "read" and user.role in [UserRole.HIRING_MANAGER, UserRole.RECRUITER]:
            return True
        
        # Interviewers can only access their own scorecards
        if user.role == UserRole.INTERVIEWER:
            # In production, check if scorecard belongs to interviewer
            return True  # Simplified for demo
        
        # Viewers have limited access
        if user.role == UserRole.VIEWER:
            return False  # Viewers cannot access individual scorecards
        
        return False
    
    def _check_session_access(self, user: User, session_id: str,
                             action: str) -> bool:
        """Check access to specific interview session."""
        # Similar logic to scorecard access
        if user.role == UserRole.ADMIN:
            return True
        
        if action == "read" and user.role in [UserRole.HIRING_MANAGER, UserRole.RECRUITER]:
            return True
        
        if user.role == UserRole.INTERVIEWER:
            # Check if user is the interviewer for this session
            return True  # Simplified for demo
        
        return False
    
    def get_accessible_resources(self, user: User, resource_type: str) -> List[str]:
        """Get list of resources user can access."""
        role_permissions = self.role_permissions.get(user.role, {})
        allowed_resources = role_permissions.get("read", [])
        
        if "all" in allowed_resources:
            return ["all"]  # User can access all resources
        
        return allowed_resources
    
    def create_default_users(self) -> None:
        """Create default users for the system."""
        # Create admin user
        self.create_user(
            username="admin",
            email="admin@eureka.ai",
            password="admin123",  # In production, use secure password
            role=UserRole.ADMIN
        )
        
        # Create hiring manager
        self.create_user(
            username="hiring_manager",
            email="hm@eureka.ai",
            password="hm123",
            role=UserRole.HIRING_MANAGER
        )
        
        # Create recruiter
        self.create_user(
            username="recruiter",
            email="recruiter@eureka.ai",
            password="rec123",
            role=UserRole.RECRUITER
        )
        
        # Create interviewer
        self.create_user(
            username="interviewer",
            email="interviewer@eureka.ai",
            password="int123",
            role=UserRole.INTERVIEWER
        )
        
        # Create viewer
        self.create_user(
            username="viewer",
            email="viewer@eureka.ai",
            password="view123",
            role=UserRole.VIEWER
        )


class AuthMiddleware:
    """Authentication middleware for API endpoints."""
    
    def __init__(self, rbac_manager: RBACManager):
        self.rbac_manager = rbac_manager
    
    def require_auth(self, required_role: Optional[UserRole] = None):
        """Decorator to require authentication."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # In a real FastAPI app, this would extract token from request
                # For now, we'll simulate the middleware behavior
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_permission(self, action: str, resource: str):
        """Decorator to require specific permission."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Check permission logic here
                return func(*args, **kwargs)
            return wrapper
        return decorator