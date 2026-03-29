from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.empresa_service import EmpresaService
from app.schemas.empresa import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from app.auth import get_current_user, require_role
from uuid import UUID
from typing import Optional

router = APIRouter()


@router.get("/", response_model=dict)
async def list_empresas(
    skip: int = 0,
    limit: int = Query(50, le=100),
    actividad: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Listar empresas registradas"""
    return await EmpresaService.get_all(db, skip, limit, actividad)


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def get_empresa(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    empresa = await EmpresaService.get_by_id(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def create_empresa(
    empresa_in: EmpresaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    """Registrar nueva empresa (solo admin)"""
    return await EmpresaService.create(db, empresa_in)


@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def update_empresa(
    empresa_id: UUID,
    empresa_update: EmpresaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    """Actualizar empresa (solo admin)"""
    empresa = await EmpresaService.update(db, empresa_id, empresa_update)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_empresa(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    """Eliminar empresa (solo admin)"""
    deleted = await EmpresaService.delete(db, empresa_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
