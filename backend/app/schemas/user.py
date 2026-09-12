from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class RoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    job_title: Optional[str] = "Enterprise User"
    department: Optional[str] = "General"
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_name: str = Field(..., description="Assigned enterprise role (e.g., Admin, Executive, Business Analyst, Data Analyst, Viewer)")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    role_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserDetailResponse(UserBase):
    id: int
    is_superuser: bool
    roles: List[RoleSchema] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserDetailResponse]
    total_count: int
    page: int
    page_size: int
