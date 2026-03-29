from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import AuditoriaStatusEnum


class AuditoriaItemCreate(BaseModel):
    empresa_id: UUID
    iso_control_ref: Optional[str] = None
    control_name: str
    activity_desc: Optional[str] = None
    status: AuditoriaStatusEnum = AuditoriaStatusEnum.pendiente
    notas: Optional[str] = None
    fecha_evaluacion: Optional[date] = None


class AuditoriaItemUpdate(BaseModel):
    control_name: Optional[str] = None
    activity_desc: Optional[str] = None
    status: Optional[AuditoriaStatusEnum] = None
    notas: Optional[str] = None
    fecha_evaluacion: Optional[date] = None


class AuditoriaItemResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    iso_control_ref: Optional[str]
    control_name: str
    activity_desc: Optional[str]
    status: str
    notas: Optional[str]
    auditor_id: Optional[UUID]
    fecha_evaluacion: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
