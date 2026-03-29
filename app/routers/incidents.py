from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.services.incident_service import IncidentService
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentStatusUpdate, IncidentStatsResponse, IncidentListResponse
from uuid import UUID
from typing import Optional

router = APIRouter()


def _empresa_filter(user: dict) -> Optional[str]:
    """Devuelve el empresa_id si el rol debe ver solo su empresa, None si ve todo."""
    if user["role"] in ("admin", "auditor"):
        return None
    return user.get("empresa_id")


@router.get("/stats", response_model=IncidentStatsResponse)
async def get_incident_stats(
    days: int = Query(30, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Métricas de incidentes: total, tasa resolución, MTTR, por severidad"""
    return await IncidentService.get_stats(db, days, empresa_id=_empresa_filter(current_user))


@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    skip: int = 0,
    limit: int = Query(20, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Listar incidentes con filtros y paginación"""
    return await IncidentService.get_all(
        db, skip, limit, status, severity, category,
        empresa_id=_empresa_filter(current_user)
    )


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reportar nuevo incidente"""
    return await IncidentService.create(db, incident_in)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Detalle de un incidente"""
    incident = await IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incident


@router.put("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: UUID,
    status_update: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cambiar estado del incidente"""
    incident = await IncidentService.update_status(db, incident_id, status_update)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incident
