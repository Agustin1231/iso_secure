from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.snapshot_service import SnapshotService
from app.schemas.snapshot import KpiSnapshotResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=KpiSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_snapshot(db: AsyncSession = Depends(get_db)):
    """Genera un snapshot manual de los KPIs actuales"""
    return await SnapshotService.create_snapshot(db)

@router.get("/", response_model=List[KpiSnapshotResponse])
async def get_snapshot_history(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el historial de snapshots para análisis de tendencias"""
    return await SnapshotService.get_history(db, limit)
