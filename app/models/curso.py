import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.enums import NivelCursoEnum


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=True)
    material_texto: Mapped[str] = mapped_column(Text, nullable=True)
    categoria: Mapped[str] = mapped_column(String(100), nullable=True)
    nivel: Mapped[NivelCursoEnum] = mapped_column(SAEnum(NivelCursoEnum), nullable=False, default=NivelCursoEnum.basico)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
