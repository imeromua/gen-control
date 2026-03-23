"""V005 adjustments and outage_schedule tables

Revision ID: v005
Revises: v004
Create Date: 2025-01-05 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "v005"
down_revision = "v004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "adjustments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("adjustment_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("value_before", sa.Numeric(12, 3), nullable=False),
        sa.Column("value_after", sa.Numeric(12, 3), nullable=False),
        sa.Column("delta", sa.Numeric(12, 3), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("document_ref", sa.String(255), nullable=True),
        sa.Column(
            "performed_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "performed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "outage_schedule",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("outage_date", sa.Date, nullable=False),
        sa.Column("hour_start", sa.SmallInteger, nullable=False),
        sa.Column("hour_end", sa.SmallInteger, nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column(
            "created_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("outage_schedule")
    op.drop_table("adjustments")
