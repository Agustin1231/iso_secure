import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, ForeignKey, DateTime, Date, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import AuditoriaStatusEnum


class AuditoriaItem(Base):
    __tablename__ = "auditoria_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    iso_control_ref: Mapped[str] = mapped_column(String(20), nullable=True)
    control_name: Mapped[str] = mapped_column(String(200), nullable=False)
    activity_desc: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[AuditoriaStatusEnum] = mapped_column(SAEnum(AuditoriaStatusEnum), nullable=False, default=AuditoriaStatusEnum.pendiente)
    notas: Mapped[str] = mapped_column(Text, nullable=True)
    auditor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    fecha_evaluacion: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
