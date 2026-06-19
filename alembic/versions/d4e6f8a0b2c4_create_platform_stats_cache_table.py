"""create platform_stats_cache table

Revision ID: d4e6f8a0b2c4
Revises: c3d5e7f9b1a2
Create Date: 2026-06-18 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "d4e6f8a0b2c4"
down_revision: Union[str, Sequence[str], None] = "c3d5e7f9b1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_stats_cache",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("leetcode_easy", sa.Integer(), nullable=True),
        sa.Column("leetcode_medium", sa.Integer(), nullable=True),
        sa.Column("leetcode_hard", sa.Integer(), nullable=True),
        sa.Column("leetcode_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("codeforces_solved", sa.Integer(), nullable=True),
        sa.Column("codeforces_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("platform_stats_cache")
