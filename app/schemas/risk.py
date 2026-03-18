from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.utils.enums import RiskLevelEnum

class RiskCreate(BaseModel):
    domain: str = Field(..., max_length=100)
    probability: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)
    # score y level se calculan automáticamente en el servicio

class RiskResponse(BaseModel):
    id: UUID
    domain: str
    level: RiskLevelEnum
    score: int
    probability: int
    impact: int
    notes: Optional[str]
    recorded_at: datetime

    model_config = {"from_attributes": True}

class RiskCurrentResponse(BaseModel):
    global_score: float
    global_level: RiskLevelEnum
    total_domains: int
    by_level: dict  # {"low": 2, "medium": 3, "high": 1, "critical": 0}
    highest_risk_domain: Optional[str]
    recorded_at: datetime

class RiskByDomainItem(BaseModel):
    domain: str
    level: RiskLevelEnum
    score: int
    probability: int
    impact: int
    recorded_at: datetime

class RiskByDomainResponse(BaseModel):
    domains: list[RiskByDomainItem]
    total: int
