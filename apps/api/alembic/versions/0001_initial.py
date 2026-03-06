"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-06
"""

import uuid

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
    )


def downgrade() -> None:
    op.drop_table("tasks")
