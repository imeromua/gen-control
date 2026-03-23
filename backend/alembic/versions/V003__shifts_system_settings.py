"""V003 shifts system_settings

Revision ID: v003
Revises: v002
Create Date: 2025-01-03 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "v003"
down_revision = "v002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("work_time_start", sa.Time(), nullable=False),
        sa.Column("work_time_end", sa.Time(), nullable=False),
        sa.Column(
            "updated_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "shifts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("shift_number", sa.Integer(), nullable=False),
        sa.Column(
            "generator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generators.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "started_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "stopped_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Numeric(10, 2), nullable=True),
        sa.Column("fuel_consumed_liters", sa.Numeric(8, 3), nullable=True),
        sa.Column("motohours_accumulated", sa.Numeric(8, 3), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("shifts")
    op.drop_table("system_settings")
