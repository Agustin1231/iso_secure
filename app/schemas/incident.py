from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.utils.enums import SeverityEnum, IncidentStatusEnum

class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=200, description="Título del incidente")
    description: Optional[str] = Field(None, description="Descripción detallada")
    severity: SeverityEnum
    category: Optional[str] = Field(None, max_length=100)
    reported_by: Optional[str] = Field(None, max_length=100)

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatusEnum
    resolved_at: Optional[datetime] = None  # Requerido si status=closed

class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    severity: SeverityEnum
    status: IncidentStatusEnum
    category: Optional[str]
    reported_by: Optional[str]
    reported_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}

class IncidentListResponse(BaseModel):
    total: int
    items: list[IncidentResponse]
    skip: int
    limit: int

class IncidentStatsResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    closed: int
    by_severity: dict  # {"low": int, "medium": int, "high": int, "critical": int}
    avg_resolution_hrs: Optional[float]
    resolution_rate_pct: float  # (closed / total) * 100
