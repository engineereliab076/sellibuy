"""create auth tables

Revision ID: f431bf170217
Revises: 42c5f0ad6aed
Create Date: 2026-06-30 14:36:45.246158

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f431bf170217"
down_revision: str | Sequence[str] | None = "42c5f0ad6aed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_user_role = PgEnum(
    "BUYER", "SUPPLIER", "AGENT", "ADMIN",
    name="user_role",
    schema="auth",
    create_type=False,
)
_user_status = PgEnum(
    "ACTIVE", "SUSPENDED", "DEACTIVATED",
    name="user_status",
    schema="auth",
    create_type=False,
)


def upgrade() -> None:
    _user_role.create(op.get_bind(), checkfirst=True)
    _user_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("role", _user_role, nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("email", CITEXT(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "status",
            _user_status,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
        schema="auth",
    )

    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("device_fingerprint", sa.Text(), nullable=False),
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            name="fk_refresh_tokens_user_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        schema="auth",
    )


def downgrade() -> None:
    op.drop_table("refresh_tokens", schema="auth")
    op.drop_table("users", schema="auth")
    _user_status.drop(op.get_bind(), checkfirst=True)
    _user_role.drop(op.get_bind(), checkfirst=True)
