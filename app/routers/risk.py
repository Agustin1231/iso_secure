from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.services.risk_service import RiskService
from app.schemas.risk import RiskCreate, RiskResponse, RiskCurrentResponse, RiskByDomainResponse
from uuid import UUID
from typing import Optional

router = APIRouter()


def _empresa_filter(user: dict) -> Optional[str]:
    if user["role"] in ("admin", "auditor"):
        return None
    return user.get("empresa_id")


@router.get("/current", response_model=RiskCurrentResponse)
async def get_current_risk(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Nivel de riesgo actual del SGSI"""
    return await RiskService.get_current_stats(db, empresa_id=_empresa_filter(current_user))


@router.get("/by-domain", response_model=RiskByDomainResponse)
async def get_risk_by_domain(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Riesgo actual desglosado por dominio"""
    return await RiskService.get_by_domain(db, empresa_id=_empresa_filter(current_user))


@router.get("/history", response_model=dict)
async def get_risk_history(
    days: int = Query(90, ge=1),
    domain: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Historial de riesgos por período"""
    return await RiskService.get_history(db, days, domain, skip, limit, empresa_id=_empresa_filter(current_user))


@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    risk_in: RiskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Registrar evaluación de riesgo"""
    return await RiskService.create(db, risk_in)
