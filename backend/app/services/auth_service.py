from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, Role
from app.models.audit import UserActivityLog
from app.schemas.auth import (
    UserLogin,
    UserRegister,
    TokenResponse,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)


class AuthService:
    @staticmethod
    def log_activity(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None,
    ) -> UserActivityLog:
        """Create an audit log record for security and compliance."""
        log = UserActivityLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            details=details,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @classmethod
    def authenticate(
        cls,
        db: Session,
        credentials: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticate user by email and password, generate JWT tokens, and log activity."""
        user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            cls.log_activity(
                db=db,
                action="LOGIN_FAILED",
                user_email=credentials.email,
                ip_address=ip_address,
                user_agent=user_agent,
                status="FAILED",
                details="Invalid email or password",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            cls.log_activity(
                db=db,
                action="LOGIN_BLOCKED",
                user_id=user.id,
                user_email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                status="FAILED",
                details="User account is deactivated",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact your system administrator.",
            )

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        # Create JWT token pair
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        # Log successful login
        cls.log_activity(
            db=db,
            action="LOGIN_SUCCESS",
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
            details=f"Roles: {', '.join(user.role_names)}",
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserOut.model_validate(user),
        )

    @classmethod
    def register(
        cls,
        db: Session,
        user_in: UserRegister,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Register a new enterprise user, assign role, and return tokens."""
        email_clean = user_in.email.lower().strip()
        existing = db.query(User).filter(User.email == email_clean).first()
        if existing:
            cls.log_activity(
                db=db,
                action="REGISTRATION_FAILED",
                user_email=email_clean,
                ip_address=ip_address,
                user_agent=user_agent,
                status="FAILED",
                details="Email already registered in platform",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

        # Find target role
        target_role_name = user_in.role_name or "Viewer"
        role = db.query(Role).filter(Role.name == target_role_name).first()
        if not role:
            # Fallback to Viewer or create
            role = db.query(Role).filter(Role.name == "Viewer").first()
            if not role:
                role = Role(
                    name="Viewer",
                    description="Default enterprise read-only viewer role",
                    permissions="view:dashboards,view:reports",
                )
                db.add(role)
                db.commit()
                db.refresh(role)

        new_user = User(
            email=email_clean,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name.strip(),
            job_title=user_in.job_title,
            department=user_in.department,
            phone_number=user_in.phone_number,
            is_active=True,
            is_superuser=False,
            roles=[role],
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate tokens
        access_token = create_access_token(subject=new_user.id)
        refresh_token = create_refresh_token(subject=new_user.id)

        # Log registration
        cls.log_activity(
            db=db,
            action="USER_REGISTERED",
            user_id=new_user.id,
            user_email=new_user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
            details=f"Assigned role: {role.name}",
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserOut.model_validate(new_user),
        )

    @classmethod
    def refresh_token(
        cls,
        db: Session,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Validate refresh token and issue new token pair."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
            )

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        cls.log_activity(
            db=db,
            action="TOKEN_REFRESHED",
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=UserOut.model_validate(user),
        )

    @classmethod
    def forgot_password(
        cls,
        db: Session,
        req: ForgotPasswordRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """Generate a password reset token for the specified user."""
        email_clean = req.email.lower().strip()
        user = db.query(User).filter(User.email == email_clean).first()
        
        # For enterprise security, always return success message even if email not found to avoid enumeration
        if user:
            reset_token = create_access_token(subject=f"reset:{user.id}", expires_delta=None)
            cls.log_activity(
                db=db,
                action="PASSWORD_RESET_REQUESTED",
                user_id=user.id,
                user_email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                status="SUCCESS",
            )
            # In a real environment, send reset email; for dev/demo we return token for instant testing
            return {
                "message": "Password reset instructions sent to email.",
                "reset_token": reset_token,  # Provided for seamless API/demo testing
            }
        
        return {"message": "Password reset instructions sent to email."}

    @classmethod
    def reset_password(
        cls,
        db: Session,
        req: ResetPasswordRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """Reset user password using valid reset token."""
        payload = decode_token(req.token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token",
            )
        
        sub = str(payload.get("sub", ""))
        if not sub.startswith("reset:"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token scope",
            )
        
        user_id = int(sub.split(":", 1)[1])
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.hashed_password = get_password_hash(req.new_password)
        db.commit()

        cls.log_activity(
            db=db,
            action="PASSWORD_RESET_COMPLETED",
            user_id=user.id,
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        return {"message": "Password has been successfully reset. Please log in with your new credentials."}
