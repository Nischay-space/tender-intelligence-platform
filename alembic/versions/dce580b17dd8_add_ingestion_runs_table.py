"""add ingestion_runs table

Revision ID: dce580b17dd8
Revises: e9375b22db4d
Create Date: 2026-08-31
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dce580b17dd8"
down_revision: Union[str, Sequence[str], None] = "e9375b22db4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ingestion_runs table for run-history tracking."""

    op.create_table(
        "ingestion_runs",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="RUNNING",
        ),
        sa.Column(
            "discovered",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "successful",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "failed",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "skipped",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_ingestion_runs_started_at",
        "ingestion_runs",
        ["started_at"],
    )


def downgrade() -> None:
    """Drop ingestion_runs table."""

    op.drop_index(
        "ix_ingestion_runs_started_at",
        table_name="ingestion_runs",
    )

    op.drop_table("ingestion_runs")