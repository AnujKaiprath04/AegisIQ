from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.audit import UserActivityLog

# Association table for User <-> Role (Many-to-Many)
UserRole = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    permissions = Column(Text, nullable=True)  # JSON or comma-separated permissions
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", secondary=UserRole, back_populates="roles")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=True, default="Enterprise User")
    department = Column(String(100), nullable=True, default="General")
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=UserRole, back_populates="users", lazy="joined")
    activity_logs = relationship("UserActivityLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email='{self.email}', full_name='{self.full_name}')>"

    @property
    def role_names(self) -> list[str]:
        """Convenience accessor for assigned role names."""
        return [role.name for role in self.roles]
