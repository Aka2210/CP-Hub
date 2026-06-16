"""create stages table

Revision ID: c3d5e7f9b1a2
Revises: a1f3e2d4c5b6
Create Date: 2026-06-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "c3d5e7f9b1a2"
down_revision: Union[str, Sequence[str], None] = "a1f3e2d4c5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("requires", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("problems", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("rewards_exp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rewards_coins", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("stages")
