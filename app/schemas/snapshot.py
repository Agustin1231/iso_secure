from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class KpiSnapshotResponse(BaseModel):
    id: UUID
    snapshot_date: date
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    critical_incidents: int
    avg_resolution_hrs: Optional[float]
    total_controls: int
    controls_compliant: int
    controls_en_proceso: int
    controls_non_compliant: int
    global_compliance_pct: Optional[float]
    global_risk_score: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}
