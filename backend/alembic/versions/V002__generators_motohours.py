"""V002 generators motohours

Revision ID: v002
Revises: v001
Create Date: 2025-01-02 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "v002"
down_revision = "v001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "generators",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "generator_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "generator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generators.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("fuel_type", sa.String(10), nullable=False, server_default="A95"),
        sa.Column("tank_capacity_liters", sa.Numeric(8, 2), nullable=True),
        sa.Column("fuel_consumption_per_hour", sa.Numeric(6, 3), nullable=True),
        sa.Column("fuel_warning_level", sa.Numeric(6, 2), nullable=True),
        sa.Column("fuel_critical_level", sa.Numeric(6, 2), nullable=True),
        sa.Column("to_interval_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("to_warning_before_hours", sa.Numeric(6, 2), nullable=True),
        sa.Column("max_continuous_work_hours", sa.Numeric(6, 2), nullable=True),
        sa.Column("max_daily_hours", sa.Numeric(6, 2), nullable=True),
        sa.Column("min_pause_between_starts_min", sa.Integer(), nullable=True),
        sa.Column("expected_consumption_deviation_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("initial_motohours", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    op.create_table(
        "event_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column(
            "generator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generators.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "performed_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "motohours_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "generator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generators.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("shift_id", UUID(as_uuid=True), nullable=True),
        sa.Column("hours_added", sa.Numeric(8, 3), nullable=False),
        sa.Column("total_after", sa.Numeric(10, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "maintenance_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "generator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generators.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "performed_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("motohours_at_service", sa.Numeric(10, 2), nullable=False),
        sa.Column("next_service_at_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("performed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("maintenance_log")
    op.drop_table("motohours_log")
    op.drop_table("event_log")
    op.drop_table("generator_settings")
    op.drop_table("generators")
