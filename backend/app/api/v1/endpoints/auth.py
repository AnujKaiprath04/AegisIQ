from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_client_ip, get_user_agent, require_roles
from app.models.user import User, Role
from app.models.audit import UserActivityLog
from app.schemas.auth import (
    UserLogin,
    UserRegister,
    TokenResponse,
    TokenRefreshRequest,
    UserOut,
    RoleOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuditLogOut,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new enterprise user",
    description="Registers a new user account, assigns the requested role (or default Viewer), and returns an access/refresh JWT token pair.",
)
def register(
    user_in: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    return AuthService.register(db=db, user_in=user_in, ip_address=ip_address, user_agent=user_agent)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Enterprise User Login",
    description="Authenticates user credentials, updates last login timestamp, logs audit event, and returns access and refresh JWT tokens.",
)
def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    return AuthService.authenticate(db=db, credentials=credentials, ip_address=ip_address, user_agent=user_agent)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Issues a fresh access token and refresh token given a valid existing refresh token.",
)
def refresh_token(
    req: TokenRefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    return AuthService.refresh_token(db=db, refresh_token=req.refresh_token, ip_address=ip_address, user_agent=user_agent)


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Returns the currently authenticated user profile with assigned enterprise roles and permissions.",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Logs out the current session and records an audit log event.",
)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    AuthService.log_activity(
        db=db,
        action="LOGOUT",
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS",
    )
    return {"message": "Successfully logged out of AegisIQ platform"}


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Initiates password reset workflow and generates recovery token.",
)
def forgot_password(
    req: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    return AuthService.forgot_password(db=db, req=req, ip_address=ip_address, user_agent=user_agent)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Complete Password Reset",
    description="Resets the user's password using the verified reset token.",
)
def reset_password(
    req: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    return AuthService.reset_password(db=db, req=req, ip_address=ip_address, user_agent=user_agent)


@router.get(
    "/roles",
    response_model=List[RoleOut],
    status_code=status.HTTP_200_OK,
    summary="List System Roles",
    description="Lists all enterprise roles configured in AegisIQ.",
)
def get_roles(
    db: Session = Depends(get_db),
):
    return db.query(Role).all()


@router.get(
    "/activity-logs",
    response_model=List[AuditLogOut],
    status_code=status.HTTP_200_OK,
    summary="Get Activity Logs",
    description="Retrieves security activity logs. Admins receive all system logs; other roles receive their own logs.",
)
def get_activity_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_admin = current_user.is_superuser or any(r.name == "Admin" for r in current_user.roles)
    query = db.query(UserActivityLog)
    if not is_admin:
        query = query.filter(UserActivityLog.user_id == current_user.id)
    
    return query.order_by(UserActivityLog.created_at.desc()).limit(limit).all()


# --- RBAC Test / Verification Endpoints ---
@router.get(
    "/test-rbac/admin-only",
    summary="RBAC Test: Admin Only",
    dependencies=[Depends(require_roles(["Admin"]))],
)
def test_admin_access(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": f"Welcome Admin {current_user.full_name}. Access granted to high-privilege operations.",
        "user_email": current_user.email,
        "roles": current_user.role_names,
    }


@router.get(
    "/test-rbac/executive-or-analyst",
    summary="RBAC Test: Executive or Analyst",
    dependencies=[Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst"]))],
)
def test_executive_analyst_access(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": f"Welcome {current_user.full_name}. Access granted to analytical/executive view.",
        "user_email": current_user.email,
        "roles": current_user.role_names,
    }
