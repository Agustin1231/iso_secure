from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.services.control_service import ControlService
from app.schemas.control import ControlCreate, ControlResponse, ControlUpdate, ComplianceResponse
from uuid import UUID
from typing import Optional

router = APIRouter()


def _empresa_filter(user: dict) -> Optional[str]:
    if user["role"] in ("admin", "auditor"):
        return None
    return user.get("empresa_id")


@router.get("/compliance", response_model=ComplianceResponse)
async def get_compliance_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """% cumplimiento global y por dominio"""
    return await ControlService.get_compliance_stats(db, empresa_id=_empresa_filter(current_user))


@router.get("/", response_model=dict)
async def list_controls(
    skip: int = 0,
    limit: int = Query(50, le=100),
    status: Optional[str] = None,
    iso_domain: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Listar controles con filtros"""
    return await ControlService.get_all(db, skip, limit, status, iso_domain, empresa_id=_empresa_filter(current_user))


@router.post("/", response_model=ControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(
    control_in: ControlCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Registrar control ISO 27001"""
    return await ControlService.create(db, control_in)


@router.put("/{control_id}", response_model=ControlResponse)
async def update_control(
    control_id: UUID,
    control_update: ControlUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Actualizar control"""
    control = await ControlService.update(db, control_id, control_update)
    if not control:
        raise HTTPException(status_code=404, detail="Control no encontrado")
    return control
