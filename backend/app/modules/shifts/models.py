import uuid
from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shift_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    generator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generators.id", ondelete="RESTRICT"), nullable=False
    )
    started_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stopped_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    fuel_consumed_liters: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    motohours_accumulated: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships — used for joinedload in repository
    generator: Mapped["Generator"] = relationship(  # type: ignore[name-defined]
        "Generator", foreign_keys=[generator_id], lazy="noload"
    )
    operator: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[started_by], lazy="noload"
    )


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_time_start: Mapped[time] = mapped_column(Time, nullable=False)
    work_time_end: Mapped[time] = mapped_column(Time, nullable=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
