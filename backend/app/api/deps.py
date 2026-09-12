from typing import Generator, List, Optional, Callable
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

# Security scheme for JWT Bearer header
security = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Extract real client IP considering reverse proxies / load balancers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def get_user_agent(request: Request) -> str:
    """Extract user agent header."""
    return request.headers.get("User-Agent", "Unknown Client")[:255]


def get_current_user(
    db: Session = Depends(get_db),
    auth_creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """Validate Bearer token and return active authenticated user."""
    if not auth_creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(auth_creds.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication token or token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in system",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Role-Based Access Control (RBAC) Dependency Factory.
    Ensures the current user possesses at least one of the specified allowed roles,
    or is a superuser.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_roles = [role.name for role in current_user.roles]
        has_permission = any(role in allowed_roles for role in user_roles)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This action requires one of the following roles: {', '.join(allowed_roles)}. Your current roles: {', '.join(user_roles) or 'None'}.",
            )
        return current_user

    return role_checker
