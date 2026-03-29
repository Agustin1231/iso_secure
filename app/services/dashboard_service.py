import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.incident_service import IncidentService
from app.services.control_service import ControlService
from app.services.risk_service import RiskService
from datetime import datetime, timezone
from sqlalchemy import select, desc, func
from app.models.incident import Incident
from app.utils.enums import IncidentStatusEnum, SeverityEnum

class DashboardService:
    @staticmethod
    def get_kpi_status(value: float, threshold_green: float, threshold_amber: float, higher_is_better: bool = True) -> str:
        if higher_is_better:
            if value >= threshold_green:
                return "green"
            elif value >= threshold_amber:
                return "amber"
            else:
                return "red"
        else:
            # Para KPIs donde menor es mejor (ej: score de riesgo, MTTR)
            if value <= threshold_green:
                return "green"
            elif value <= threshold_amber:
                return "amber"
            else:
                return "red"

    @staticmethod
    async def get_summary(db: AsyncSession, empresa_id: str = None):
        # SQLAlchemy AsyncSession no permite operaciones concurrentes en la misma sesión
        # Ejecutamos secuencialmente por seguridad
        incident_stats = await IncidentService.get_stats(db, days=365, empresa_id=empresa_id)
        control_stats = await ControlService.get_compliance_stats(db, empresa_id=empresa_id)
        risk_stats = await RiskService.get_current_stats(db, empresa_id=empresa_id)

        # Adicional: contar incidentes críticos activos para el dashboard
        empresa_filter = (Incident.empresa_id == empresa_id,) if empresa_id else ()
        critical_active_stmt = select(func.count(Incident.id)).where(
            Incident.severity == SeverityEnum.critical,
            Incident.status != IncidentStatusEnum.closed,
            *empresa_filter
        )
        critical_active = (await db.execute(critical_active_stmt)).scalar() if hasattr(Incident, 'severity') else 0
        
        # Si por alguna razón incident_stats no tiene severity, lo recalcula (especificación pide críticos activos)
        # En incident_service.get_stats ya tenemos un breakdown pero de los últimos N días.
        # Aquí queremos críticos activos (reales en sistema).
        
        return {
            "generated_at": datetime.now(timezone.utc),
            "incidents_total": incident_stats["total"],
            "incidents_open": incident_stats["open"],
            "incidents_in_progress": incident_stats["in_progress"],
            "incidents_closed": incident_stats["closed"],
            "incidents_critical_active": critical_active or 0,
            "incidents_avg_resolution_hrs": incident_stats["avg_resolution_hrs"],
            "incidents_resolution_rate_pct": incident_stats["resolution_rate_pct"],
            "controls_total": control_stats["total_controls"],
            "controls_compliant": control_stats["compliant"],
            "controls_non_compliant": control_stats["non_compliant"],
            "controls_global_compliance_pct": control_stats["global_compliance_pct"],
            "risk_global_score": risk_stats["global_score"],
            "risk_global_level": risk_stats["global_level"],
            "risk_highest_domain": risk_stats["highest_risk_domain"]
        }

    @staticmethod
    async def get_kpis(db: AsyncSession, empresa_id: str = None):
        summary = await DashboardService.get_summary(db, empresa_id=empresa_id)
        
        kpis = [
            {
                "name": "Tasa de Resolución de Incidentes",
                "value": summary["incidents_resolution_rate_pct"],
                "unit": "%",
                "status": DashboardService.get_kpi_status(summary["incidents_resolution_rate_pct"], 80.0, 60.0),
                "threshold_green": 80.0,
                "threshold_amber": 60.0,
                "description": "Porcentaje de incidentes cerrados sobre el total"
            },
            {
                "name": "Cumplimiento de Controles ISO",
                "value": summary["controls_global_compliance_pct"],
                "unit": "%",
                "status": DashboardService.get_kpi_status(summary["controls_global_compliance_pct"], 85.0, 70.0),
                "threshold_green": 85.0,
                "threshold_amber": 70.0,
                "description": "Porcentaje de controles en estado compliant"
            },
            {
                "name": "Score de Riesgo Global",
                "value": summary["risk_global_score"] or 0.0,
                "unit": "score",
                "status": DashboardService.get_kpi_status(summary["risk_global_score"] or 0.0, 6.0, 10.0, False),
                "threshold_green": 6.0,
                "threshold_amber": 10.0,
                "description": "Promedio del score de riesgo (probabilidad x impacto) por dominio"
            },
            {
                "name": "MTTR (Tiempo Medio de Resolución)",
                "value": summary["incidents_avg_resolution_hrs"] or 0.0,
                "unit": "horas",
                "status": DashboardService.get_kpi_status(summary["incidents_avg_resolution_hrs"] or 0.0, 24.0, 48.0, False),
                "threshold_green": 24.0,
                "threshold_amber": 48.0,
                "description": "Promedio de horas para resolver un incidente"
            }
        ]
        
        return {
            "generated_at": summary["generated_at"],
            "kpis": kpis
        }

    @staticmethod
    async def get_export(db: AsyncSession):
        summary = await DashboardService.get_summary(db)
        kpis = await DashboardService.get_kpis(db)
        
        # Get recent incidents (last 10)
        recent_result = await db.execute(select(Incident).order_by(Incident.reported_at.desc()).limit(10))
        recent_incidents = recent_result.scalars().all()
        
        # Get full compliance and risk
        compliance = await ControlService.get_compliance_stats(db)
        risk_by_domain = await RiskService.get_by_domain(db)
        
        return {
            "format": "json",
            "generated_at": datetime.now(timezone.utc),
            "data": {
                "summary": summary,
                "kpis": kpis["kpis"],
                "incidents": {
                    "stats": await IncidentService.get_stats(db, days=365),
                    "recent": recent_incidents
                },
                "controls": {
                    "compliance": compliance
                },
                "risk": {
                    "current": await RiskService.get_current_stats(db),
                    "by_domain": risk_by_domain
                }
            }
        }
