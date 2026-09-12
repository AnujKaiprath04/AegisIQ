from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.user import (
    RoleSchema,
    UserCreate,
    UserDetailResponse,
    UserListResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Enterprise User Management"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Paginated list of enterprise users with role & department filters."""
    skip = (page - 1) * page_size
    users, total_count = UserService.get_users(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        role_filter=role,
        department_filter=department,
    )
    return UserListResponse(
        users=[UserDetailResponse.model_validate(u) for u in users],
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Create a new user with designated enterprise role and department."""
    new_user = UserService.create_user(db=db, user_in=user_in, actor_email=current_user.email)
    return UserDetailResponse.model_validate(new_user)


@router.get("/roles", response_model=List[RoleSchema])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all enterprise roles and their permissions."""
    roles = UserService.get_roles(db=db)
    return [RoleSchema.model_validate(r) for r in roles]


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Retrieve user profile details."""
    user = UserService.get_user_by_id(db=db, user_id=user_id)
    return UserDetailResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserDetailResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Update user information, roles, or active status."""
    updated = UserService.update_user(
        db=db,
        user_id=user_id,
        user_update=user_update,
        actor_email=current_user.email,
    )
    return UserDetailResponse.model_validate(updated)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Deactivate or remove user."""
    UserService.delete_user(db=db, user_id=user_id, actor_email=current_user.email)
    return {"message": f"User with ID {user_id} successfully deleted from enterprise directory."}
