import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import ProgresoEnum


class CursoProgreso(Base):
    __tablename__ = "curso_progreso"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curso_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[ProgresoEnum] = mapped_column(SAEnum(ProgresoEnum), nullable=False, default=ProgresoEnum.pendiente)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
