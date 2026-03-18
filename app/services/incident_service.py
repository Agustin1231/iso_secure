from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentStatusUpdate
from app.utils.enums import IncidentStatusEnum
from datetime import datetime, timezone, timedelta
from uuid import UUID

class IncidentService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 20, status: str = None, severity: str = None, category: str = None):
        query = select(Incident).order_by(Incident.reported_at.desc())
        
        if status:
            query = query.where(Incident.status == status)
        if severity:
            query = query.where(Incident.severity == severity)
        if category:
            query = query.where(Incident.category == category)
            
        # Count total
        total_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(total_query)).scalar()
        
        # Paging
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Manual serialization for maximum stability
        serialized_items = []
        for inc in items:
            serialized_items.append({
                "id": str(inc.id),
                "title": inc.title,
                "description": inc.description,
                "severity": inc.severity.value if hasattr(inc.severity, "value") else str(inc.severity),
                "status": inc.status.value if hasattr(inc.status, "value") else str(inc.status),
                "category": inc.category,
                "reported_by": inc.reported_by,
                "reported_at": inc.reported_at.isoformat() if inc.reported_at else None,
                "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
            })
            
        return {
            "total": total, 
            "items": serialized_items, 
            "skip": skip, 
            "limit": limit
        }

    @staticmethod
    async def create(db: AsyncSession, incident_in: IncidentCreate):
        db_incident = Incident(**incident_in.model_dump())
        db.add(db_incident)
        await db.commit()
        await db.refresh(db_incident)
        return db_incident

    @staticmethod
    async def get_by_id(db: AsyncSession, incident_id: UUID):
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_status(db: AsyncSession, incident_id: UUID, status_update: IncidentStatusUpdate):
        db_incident = await IncidentService.get_by_id(db, incident_id)
        if not db_incident:
            return None
            
        db_incident.status = status_update.status
        if status_update.status == IncidentStatusEnum.closed:
            db_incident.resolved_at = status_update.resolved_at or datetime.now(timezone.utc)
        else:
            db_incident.resolved_at = None
            
        await db.commit()
        await db.refresh(db_incident)
        return db_incident

    @staticmethod
    async def get_stats(db: AsyncSession, days: int = 30):
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Base query for stats
        base_query = select(Incident).where(Incident.reported_at >= since_date)
        
        # Total, and by status
        total_stmt = select(func.count()).select_from(base_query.subquery())
        total = (await db.execute(total_stmt)).scalar() or 0
        
        open_stmt = select(func.count()).where(and_(Incident.reported_at >= since_date, Incident.status == IncidentStatusEnum.open))
        open_count = (await db.execute(open_stmt)).scalar() or 0
        
        progress_stmt = select(func.count()).where(and_(Incident.reported_at >= since_date, Incident.status == IncidentStatusEnum.in_progress))
        in_progress = (await db.execute(progress_stmt)).scalar() or 0
        
        closed_stmt = select(func.count()).where(and_(Incident.reported_at >= since_date, Incident.status == IncidentStatusEnum.closed))
        closed = (await db.execute(closed_stmt)).scalar() or 0
        
        # By severity
        severity_result = await db.execute(
            select(Incident.severity, func.count())
            .where(Incident.reported_at >= since_date)
            .group_by(Incident.severity)
        )
        # Asegurar que las llaves sean strings para serialización JSON
        by_severity = {getattr(s, 'value', s): count for s, count in severity_result.all()}
        # Ensure all severities exist in dict
        for s in ["low", "medium", "high", "critical"]:
            by_severity.setdefault(s, 0)
            
        # Avg resolution time (hours)
        avg_res_query = select(func.avg(
            func.extract('epoch', Incident.resolved_at - Incident.reported_at) / 3600
        )).where(and_(
            Incident.reported_at >= since_date, 
            Incident.status == IncidentStatusEnum.closed, 
            Incident.resolved_at.isnot(None)
        ))
        
        avg_resolution_hrs = (await db.execute(avg_res_query)).scalar()
        
        resolution_rate_pct = (closed / total * 100) if total > 0 else 0.0
        
        # Consistent response with manual serialization for strings/floats
        return {
            "total": int(total),
            "open": int(open_count),
            "in_progress": int(in_progress),
            "closed": int(closed),
            "by_severity": by_severity,
            "avg_resolution_hrs": round(float(avg_resolution_hrs), 2) if avg_resolution_hrs else 0.0,
            "resolution_rate_pct": round(float(resolution_rate_pct), 2)
        }
