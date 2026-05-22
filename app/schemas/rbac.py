from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ─── Permisos ─────────────────────────────────────────────────────────────────
class PermissionCreate(BaseModel):
    codigo: str = Field(..., max_length=100, description="Identificador único, ej: incidents.manage")
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = Field(None, max_length=400)
    modulo: str = Field("general", max_length=60)


class PermissionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=400)
    modulo: Optional[str] = Field(None, max_length=60)


class PermissionResponse(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    descripcion: Optional[str]
    modulo: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Roles ────────────────────────────────────────────────────────────────────
class RoleCreate(BaseModel):
    nombre: str = Field(..., max_length=80)
    descripcion: Optional[str] = Field(None, max_length=300)
    permission_ids: list[UUID] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=300)
    permission_ids: Optional[list[UUID]] = None


class RoleResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str]
    es_sistema: bool
    permissions: list[PermissionResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Asignación de roles a usuarios ───────────────────────────────────────────
class UserRoleAssign(BaseModel):
    role_id: UUID


class UserRoleResponse(BaseModel):
    id: UUID
    role_id: UUID
    role_nombre: Optional[str] = None
    user_profile_id: UUID
    empresa_id: Optional[UUID] = None
    assigned_by: Optional[UUID] = None
    created_at: datetime
