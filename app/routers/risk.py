from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.risk_service import RiskService
from app.schemas.risk import RiskCreate, RiskResponse, RiskCurrentResponse, RiskByDomainResponse
from uuid import UUID
from typing import Optional

router = APIRouter()

@router.get("/current", response_model=RiskCurrentResponse)
async def get_current_risk(db: AsyncSession = Depends(get_db)):
    """Nivel de riesgo actual del SGSI"""
    return await RiskService.get_current_stats(db)

@router.get("/by-domain", response_model=RiskByDomainResponse)
async def get_risk_by_domain(db: AsyncSession = Depends(get_db)):
    """Riesgo actual desglosado por dominio"""
    return await RiskService.get_by_domain(db)

@router.get("/history", response_model=dict)
async def get_risk_history(
    days: int = Query(90, ge=1),
    domain: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Historial de riesgos por período"""
    return await RiskService.get_history(db, days, domain, skip, limit)

@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(risk_in: RiskCreate, db: AsyncSession = Depends(get_db)):
    """Registrar evaluación de riesgo"""
    return await RiskService.create(db, risk_in)
