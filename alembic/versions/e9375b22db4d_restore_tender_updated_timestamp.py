"""restore tender updated timestamp

Revision ID: e9375b22db4d
Revises: cc03b14d7866
Create Date: 2026-08-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e9375b22db4d"
down_revision: Union[str, Sequence[str], None] = "cc03b14d7866"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Restore updated_at column on tenders."""

    op.add_column(
        "tenders",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE tenders
        SET updated_at = created_at
        WHERE updated_at IS NULL
        """
    )

    op.alter_column(
        "tenders",
        "updated_at",
        nullable=False,
    )


def downgrade() -> None:
    """Remove updated_at column from tenders."""

    op.drop_column(
        "tenders",
        "updated_at",
    )