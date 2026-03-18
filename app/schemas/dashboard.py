from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DashboardSummaryResponse(BaseModel):
    generated_at: datetime
    # Bloque incidentes
    incidents_total: int
    incidents_open: int
    incidents_in_progress: int
    incidents_closed: int
    incidents_critical_active: int
    incidents_avg_resolution_hrs: Optional[float]
    incidents_resolution_rate_pct: float
    # Bloque controles
    controls_total: int
    controls_compliant: int
    controls_non_compliant: int
    controls_global_compliance_pct: float
    # Bloque riesgo
    risk_global_score: Optional[float]
    risk_global_level: Optional[str]
    risk_highest_domain: Optional[str]

class KpiItem(BaseModel):
    name: str
    value: float
    unit: str
    status: str   # "green" | "amber" | "red"
    threshold_green: float
    threshold_amber: float
    description: str

class DashboardKpisResponse(BaseModel):
    generated_at: datetime
    kpis: list[KpiItem]

class DashboardExportResponse(BaseModel):
    format: str
    generated_at: datetime
    data: dict
