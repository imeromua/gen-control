import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class OilStock(Base):
    __tablename__ = "oil_stock"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generators.id", ondelete="CASCADE"), nullable=False
    )
    oil_type: Mapped[str] = mapped_column(String(100), nullable=False)
    current_quantity: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False, default=0)
    unit: Mapped[str] = mapped_column(String(10), nullable=False, default="LITERS")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
