"""create database schemas

Revision ID: 42c5f0ad6aed
Revises: fad9c3e1fc75
Create Date: 2026-06-27 11:57:11.068757

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '42c5f0ad6aed'
down_revision: Union[str, Sequence[str], None] = 'fad9c3e1fc75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMAS = [
    "auth",
    "shared",
    "agents",
    "suppliers",
    "products",
    "procurement",
    "orders",
    "inspections",
    "payments",
    "disputes",
    "notifications",
]


def upgrade() -> None:
    """Create application schemas."""
    for schema in SCHEMAS:
        op.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')


def downgrade() -> None:
    """Drop application schemas."""
    for schema in reversed(SCHEMAS):
        op.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
