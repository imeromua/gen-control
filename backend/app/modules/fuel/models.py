import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class FuelStock(Base):
    __tablename__ = "fuel_stock"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fuel_type: Mapped[str] = mapped_column(String(20), nullable=False)
    current_liters: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False, default=0)
    max_limit_liters: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False, default=200)
    warning_level_liters: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False, default=20)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FuelDelivery(Base):
    __tablename__ = "fuel_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fuel_type: Mapped[str] = mapped_column(String(20), nullable=False)
    liters: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    check_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    delivered_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    stock_before: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    stock_after: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class FuelRefill(Base):
    __tablename__ = "fuel_refills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generators.id", ondelete="CASCADE"), nullable=False
    )
    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    liters: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    tank_level_before: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    tank_level_after: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    stock_before: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    stock_after: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    refilled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
