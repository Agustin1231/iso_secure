from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.snapshot import KpiSnapshot
from app.services.dashboard_service import DashboardService
from datetime import date, datetime, timezone
from typing import List

class SnapshotService:
    @staticmethod
    async def create_snapshot(db: AsyncSession) -> KpiSnapshot:
        """
        Captura el estado actual de los KPIs y lo guarda en la tabla kpi_snapshots.
        Si ya existe un snapshot para hoy, lo actualiza.
        """
        # Obtener datos consolidados del DashboardService
        summary = await DashboardService.get_summary(db)
        
        today = date.today()
        
        # Verificar si ya existe para hoy
        stmt = select(KpiSnapshot).where(KpiSnapshot.snapshot_date == today)
        result = await db.execute(stmt)
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            snapshot = KpiSnapshot(snapshot_date=today)
            db.add(snapshot)
            
        # Actualizar campos
        snapshot.total_incidents = summary["incidents_total"]
        snapshot.open_incidents = summary["incidents_open"]
        snapshot.resolved_incidents = summary["incidents_closed"]
        snapshot.critical_incidents = summary["incidents_critical_active"]
        snapshot.avg_resolution_hrs = summary["incidents_avg_resolution_hrs"]
        snapshot.total_controls = summary["controls_total"]
        snapshot.controls_compliant = summary["controls_compliant"]
        snapshot.controls_non_compliant = summary["controls_non_compliant"]
        # Nota: summary no tiene 'partial' explícitamente en el retorno principal de mapping, 
        # pero podemos calcularlo o sacarlo del control_stats si fuera necesario.
        # Por simplicidad y consistencia con el summary_response:
        snapshot.global_compliance_pct = summary["controls_global_compliance_pct"]
        snapshot.global_risk_score = summary["risk_global_score"]
        snapshot.created_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    @staticmethod
    async def get_history(db: AsyncSession, limit: int = 30) -> List[KpiSnapshot]:
        """Recupera los últimos N snapshots para análisis de tendencias"""
        stmt = select(KpiSnapshot).order_by(desc(KpiSnapshot.snapshot_date)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
