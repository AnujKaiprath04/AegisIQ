import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from fastapi import HTTPException, status

from app.models.user import User, Role
from app.models.audit import UserActivityLog
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

logger = logging.getLogger("aegisiq.user_service")


class UserService:
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        role_filter: Optional[str] = None,
        department_filter: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """Fetch users with optional search, role, and department filtering."""
        query = db.query(User)

        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_fmt),
                    User.email.ilike(search_fmt),
                    User.job_title.ilike(search_fmt),
                )
            )

        if department_filter:
            query = query.filter(User.department == department_filter)

        if role_filter:
            query = query.join(User.roles).filter(Role.name == role_filter)

        total_count = query.count()
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        return users, total_count

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found in enterprise registry.",
            )
        return user

    @staticmethod
    def create_user(db: Session, user_in: UserCreate, actor_email: str) -> User:
        """Create a new enterprise user with specified role and log audit trail."""
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A user with email '{user_in.email}' already exists.",
            )

        role = db.query(Role).filter(Role.name == user_in.role_name).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{user_in.role_name}' is not recognized in system role catalog.",
            )

        new_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            job_title=user_in.job_title or "Enterprise User",
            department=user_in.department or "General",
            phone_number=user_in.phone_number,
            is_active=user_in.is_active if user_in.is_active is not None else True,
            is_superuser=(user_in.role_name == "Admin"),
            roles=[role],
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Audit Log
        audit = UserActivityLog(
            user_id=new_user.id,
            user_email=actor_email,
            action="USER_CREATED",
            status="SUCCESS",
            details=f"Admin created user {new_user.email} with role {role.name}",
        )
        db.add(audit)
        db.commit()

        logger.info(f"Admin '{actor_email}' created user '{new_user.email}' with role '{role.name}'.")
        return new_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate, actor_email: str) -> User:
        """Update user profile, status, or role."""
        user = UserService.get_user_by_id(db, user_id)

        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.job_title is not None:
            user.job_title = user_update.job_title
        if user_update.department is not None:
            user.department = user_update.department
        if user_update.phone_number is not None:
            user.phone_number = user_update.phone_number
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)

        if user_update.role_name:
            role = db.query(Role).filter(Role.name == user_update.role_name).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role '{user_update.role_name}' is not recognized.",
                )
            user.roles = [role]
            user.is_superuser = (user_update.role_name == "Admin")

        db.commit()
        db.refresh(user)

        # Audit Log
        audit = UserActivityLog(
            user_id=user.id,
            user_email=actor_email,
            action="USER_UPDATED",
            status="SUCCESS",
            details=f"Updated profile/roles for {user.email}",
        )
        db.add(audit)
        db.commit()

        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, actor_email: str) -> bool:
        """Deactivate or remove user."""
        user = UserService.get_user_by_id(db, user_id)
        if user.email == actor_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot delete their own active account.",
            )

        db.delete(user)
        db.commit()

        audit = UserActivityLog(
            user_id=None,
            user_email=actor_email,
            action="USER_DELETED",
            status="SUCCESS",
            details=f"Deleted user with ID {user_id}",
        )
        db.add(audit)
        db.commit()
        return True

    @staticmethod
    def get_roles(db: Session) -> List[Role]:
        return db.query(Role).all()
