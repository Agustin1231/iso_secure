from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardSummaryResponse, DashboardKpisResponse, DashboardExportResponse

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Resumen ejecutivo consolidado"""
    return await DashboardService.get_summary(db)

@router.get("/kpis", response_model=DashboardKpisResponse)
async def get_dashboard_kpis(db: AsyncSession = Depends(get_db)):
    """KPIs con semáforo verde/ámbar/rojo"""
    return await DashboardService.get_kpis(db)

@router.get("/export", response_model=DashboardExportResponse)
async def export_dashboard(format: str = Query("json"), db: AsyncSession = Depends(get_db)):
    """Exportar todos los datos en JSON"""
    return await DashboardService.get_export(db)
