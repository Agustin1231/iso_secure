from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.utils.enums import NivelCursoEnum, ProgresoEnum


class CursoCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    video_url: Optional[str] = None
    material_texto: Optional[str] = None
    categoria: Optional[str] = None
    nivel: NivelCursoEnum = NivelCursoEnum.basico


class CursoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    video_url: Optional[str] = None
    material_texto: Optional[str] = None
    categoria: Optional[str] = None
    nivel: Optional[NivelCursoEnum] = None


class CursoResponse(BaseModel):
    id: UUID
    titulo: str
    descripcion: Optional[str]
    video_url: Optional[str]
    material_texto: Optional[str]
    categoria: Optional[str]
    nivel: str
    created_at: datetime

    class Config:
        from_attributes = True


class CursoWithProgreso(CursoResponse):
    progreso: Optional[str] = "pendiente"


class ProgresoUpdate(BaseModel):
    status: ProgresoEnum
