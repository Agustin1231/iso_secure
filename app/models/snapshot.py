import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Integer, Date, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    total_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    resolved_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_incidents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_resolution_hrs: Mapped[float] = mapped_column(Numeric(8, 2, asdecimal=False), nullable=True)
    total_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controls_compliant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controls_partial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    controls_non_compliant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    global_compliance_pct: Mapped[float] = mapped_column(Numeric(5, 2, asdecimal=False), nullable=True)
    global_risk_score: Mapped[float] = mapped_column(Numeric(5, 2, asdecimal=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
