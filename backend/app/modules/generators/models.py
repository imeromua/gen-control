import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Numeric, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.motohours.models import MotohoursLog, MaintenanceLog


class Generator(Base):
    __tablename__ = "generators"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    settings: Mapped["GeneratorSettings"] = relationship(
        "GeneratorSettings", back_populates="generator", uselist=False
    )
    motohours_logs: Mapped[list["MotohoursLog"]] = relationship(
        "MotohoursLog", back_populates="generator"
    )
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        "MaintenanceLog", back_populates="generator"
    )


class GeneratorSettings(Base):
    __tablename__ = "generator_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generators.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    fuel_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tank_capacity_liters: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    fuel_consumption_per_hour: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    fuel_warning_level: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    fuel_critical_level: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    to_interval_hours: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    to_warning_before_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_continuous_work_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_daily_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    min_pause_between_starts_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_consumption_deviation_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    initial_motohours: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=0)
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
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

