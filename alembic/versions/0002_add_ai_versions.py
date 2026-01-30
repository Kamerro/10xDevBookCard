"""add ai versions

Revision ID: 0002_add_ai_versions
Revises: 0001_initial
Create Date: 2026-01-30

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0002_add_ai_versions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "book_ai_analyses",
        sa.Column("analysis_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "book_ai_analyses",
        sa.Column("requested_version", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("book_ai_analyses", "requested_version")
    op.drop_column("book_ai_analyses", "analysis_version")
