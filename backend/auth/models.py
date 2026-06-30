"""SQLAlchemy ORM models for the auth schema."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db.base import Base
from shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(enum.StrEnum):
    BUYER = "BUYER"
    SUPPLIER = "SUPPLIER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"


class UserStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents an authenticated user account."""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", schema="auth"),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", schema="auth"),
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default="ACTIVE",
    )
    token_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(UUIDPrimaryKeyMixin, Base):
    """Tracks issued refresh tokens for rotation and revocation."""

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    device_fingerprint: Mapped[str] = mapped_column(Text, nullable=False)
    token_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
