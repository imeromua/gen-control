"""V004 fuel and oil tables

Revision ID: v004
Revises: v003
Create Date: 2025-01-04 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "v004"
down_revision = "v003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fuel_stock",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("fuel_type", sa.String(20), nullable=False),
        sa.Column("current_liters", sa.Numeric(10, 3), nullable=False, server_default="0"),
        sa.Column("max_limit_liters", sa.Numeric(10, 3), nullable=False, server_default="200"),
        sa.Column("warning_level_liters", sa.Numeric(10, 3), nullable=False, server_default="20"),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "fuel_deliveries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("fuel_type", sa.String(20), nullable=False),
        sa.Column("liters", sa.Numeric(10, 3), nullable=False),
        sa.Column("check_number", sa.String(100), nullable=True),
        sa.Column("delivered_by_name", sa.String(255), nullable=True),
        sa.Column(
            "accepted_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("stock_before", sa.Numeric(10, 3), nullable=False),
        sa.Column("stock_after", sa.Numeric(10, 3), nullable=False),
        sa.Column(
            "delivered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "fuel_refills",
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
        sa.Column("liters", sa.Numeric(8, 3), nullable=False),
        sa.Column("tank_level_before", sa.Numeric(8, 3), nullable=False),
        sa.Column("tank_level_after", sa.Numeric(8, 3), nullable=False),
        sa.Column("stock_before", sa.Numeric(10, 3), nullable=False),
        sa.Column("stock_after", sa.Numeric(10, 3), nullable=False),
        sa.Column(
            "refilled_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "oil_stock",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "generator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("generators.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("oil_type", sa.String(100), nullable=False),
        sa.Column("current_quantity", sa.Numeric(8, 3), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(10), nullable=False, server_default="LITERS"),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("oil_stock")
    op.drop_table("fuel_refills")
    op.drop_table("fuel_deliveries")
    op.drop_table("fuel_stock")
