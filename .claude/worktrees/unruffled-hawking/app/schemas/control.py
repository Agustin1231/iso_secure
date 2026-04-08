from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from app.utils.enums import ControlStatusEnum

class ControlCreate(BaseModel):
    iso_domain: str = Field(..., max_length=10, description="Ej: A.5, A.9")
    iso_control_ref: Optional[str] = Field(None, max_length=20)
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: ControlStatusEnum
    compliance_pct: float = Field(..., ge=0.0, le=100.0)
    responsible: Optional[str] = Field(None, max_length=100)
    last_reviewed: Optional[date] = None

class ControlUpdate(BaseModel):
    status: Optional[ControlStatusEnum] = None
    compliance_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    responsible: Optional[str] = None
    last_reviewed: Optional[date] = None
    description: Optional[str] = None

class ControlResponse(BaseModel):
    id: UUID
    iso_domain: str
    iso_control_ref: Optional[str]
    name: str
    description: Optional[str]
    status: ControlStatusEnum
    compliance_pct: float
    responsible: Optional[str]
    last_reviewed: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ComplianceResponse(BaseModel):
    total_controls: int
    compliant: int
    en_proceso: int
    non_compliant: int
    global_compliance_pct: float
    by_domain: dict  # {"A.5": {"compliant": 3, "total": 4, "pct": 75.0}, ...}
