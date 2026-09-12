from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# --- Role Schemas ---
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None


class RoleOut(RoleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2, max_length=100)
    job_title: Optional[str] = "Business Analyst"
    department: Optional[str] = "Analytics"
    phone_number: Optional[str] = None
    role_name: Optional[str] = Field("Viewer", description="Requested initial role: Admin, Executive, Business Analyst, Data Analyst, Viewer")


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    job_title: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    roles: List[RoleOut] = []
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Token Schemas ---
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role_names: List[str] = []


# --- Password Recovery Schemas ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# --- Audit Log Schemas ---
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
