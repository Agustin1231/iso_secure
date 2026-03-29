from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardSummaryResponse, DashboardKpisResponse, DashboardExportResponse
from typing import Optional

router = APIRouter()


def _empresa_filter(user: dict) -> Optional[str]:
    if user["role"] in ("admin", "auditor"):
        return None
    return user.get("empresa_id")


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Resumen ejecutivo consolidado"""
    return await DashboardService.get_summary(db, empresa_id=_empresa_filter(current_user))


@router.get("/kpis", response_model=DashboardKpisResponse)
async def get_dashboard_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """KPIs con semáforo verde/ámbar/rojo"""
    return await DashboardService.get_kpis(db, empresa_id=_empresa_filter(current_user))


@router.get("/export", response_model=DashboardExportResponse)
async def export_dashboard(
    format: str = Query("json"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Exportar todos los datos en JSON"""
    return await DashboardService.get_export(db)
