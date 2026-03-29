import uuid
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import String, Date, Numeric, DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import ControlStatusEnum

class Control(Base):
    __tablename__ = "controls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True, index=True)
    iso_domain: Mapped[str] = mapped_column(String(10), nullable=False)
    iso_control_ref: Mapped[str] = mapped_column(String(20), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[ControlStatusEnum] = mapped_column(SAEnum(ControlStatusEnum), nullable=False)
    compliance_pct: Mapped[float] = mapped_column(Numeric(5, 2, asdecimal=False), nullable=False, default=0.0)
    responsible: Mapped[str] = mapped_column(String(100), nullable=True)
    last_reviewed: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
