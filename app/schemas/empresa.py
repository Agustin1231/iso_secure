from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class EmpresaCreate(BaseModel):
    nombre: str = Field(..., max_length=200)
    tipo_empresa: str = Field(..., max_length=100, description="Ej: SAS, SA, Ltda, Natural")
    actividad_economica: str = Field(..., max_length=200, description="Ej: Salud, Alimentos, Tecnologia, Financiero")
    representante_legal: str = Field(..., max_length=150)
    email: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=50)
    nit: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=300)


class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    tipo_empresa: Optional[str] = Field(None, max_length=100)
    actividad_economica: Optional[str] = Field(None, max_length=200)
    representante_legal: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=50)
    nit: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=300)


class EmpresaResponse(BaseModel):
    id: UUID
    nombre: str
    tipo_empresa: str
    actividad_economica: str
    representante_legal: str
    email: Optional[str]
    telefono: Optional[str]
    nit: Optional[str]
    direccion: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
