import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Generator(Base):
    __tablename__ = "generators"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    settings: Mapped["GeneratorSettings"] = relationship(
        "GeneratorSettings", back_populates="generator", uselist=False, cascade="all, delete-orphan"
    )


class GeneratorSettings(Base):
    __tablename__ = "generator_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generators.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    fuel_type: Mapped[str] = mapped_column(String(10), nullable=False, default="A95")
    tank_capacity_liters: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    fuel_consumption_per_hour: Mapped[Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    fuel_warning_level: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    fuel_critical_level: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    to_interval_hours: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    to_warning_before_hours: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_continuous_work_hours: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_daily_hours: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    min_pause_between_starts_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_consumption_deviation_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    initial_motohours: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    generator: Mapped["Generator"] = relationship("Generator", back_populates="settings")


class EventLog(Base):
    __tablename__ = "event_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    generator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generators.id", ondelete="SET NULL"), nullable=True
    )
    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
