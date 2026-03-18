from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.control import Control
from app.schemas.control import ControlCreate, ControlUpdate
from app.utils.enums import ControlStatusEnum
from datetime import datetime, timezone
from uuid import UUID

class ControlService:
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 50, status: str = None, iso_domain: str = None):
        query = select(Control).order_by(Control.iso_domain.asc(), Control.iso_control_ref.asc())
        
        if status:
            query = query.where(Control.status == status)
        if iso_domain:
            query = query.where(Control.iso_domain == iso_domain)
            
        # Count total
        total_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(total_query)).scalar()
        
        # Paging
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Manual serialization for stability
        serialized_items = []
        for c in items:
            serialized_items.append({
                "id": str(c.id),
                "iso_domain": c.iso_domain,
                "iso_control_ref": c.iso_control_ref,
                "name": c.name,
                "description": c.description,
                "status": c.status.value if hasattr(c.status, 'value') else c.status,
                "compliance_pct": float(c.compliance_pct),
                "responsible": c.responsible,
                "last_reviewed": c.last_reviewed.isoformat() if c.last_reviewed else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None
            })
            
        return {"total": total, "items": serialized_items}

    @staticmethod
    async def create(db: AsyncSession, control_in: ControlCreate):
        db_control = Control(**control_in.model_dump())
        db.add(db_control)
        await db.commit()
        await db.refresh(db_control)
        return db_control

    @staticmethod
    async def get_by_id(db: AsyncSession, control_id: UUID):
        result = await db.execute(select(Control).where(Control.id == control_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, control_id: UUID, control_update: ControlUpdate):
        db_control = await ControlService.get_by_id(db, control_id)
        if not db_control:
            return None
            
        update_data = control_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_control, field, value)
            
        db_control.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_control)
        return db_control

    @staticmethod
    async def get_compliance_stats(db: AsyncSession):
        # Overall counters
        total = (await db.execute(select(func.count(Control.id)))).scalar() or 0
        if total == 0:
            return {
                "total_controls": 0,
                "compliant": 0,
                "partial": 0,
                "non_compliant": 0,
                "global_compliance_pct": 0.0,
                "by_domain": {}
            }
            
        compliant = (await db.execute(select(func.count(Control.id)).where(Control.status == ControlStatusEnum.compliant))).scalar() or 0
        partial = (await db.execute(select(func.count(Control.id)).where(Control.status == ControlStatusEnum.partial))).scalar() or 0
        non_compliant = (await db.execute(select(func.count(Control.id)).where(Control.status == ControlStatusEnum.non_compliant))).scalar() or 0
        
        global_compliance_pct = (compliant / total) * 100
        
        # Stats by domain
        domain_result = await db.execute(
            select(
                Control.iso_domain,
                func.count(Control.id).label("total"),
                func.count(Control.id).filter(Control.status == ControlStatusEnum.compliant).label("compliant"),
                func.count(Control.id).filter(Control.status == ControlStatusEnum.partial).label("partial"),
                func.count(Control.id).filter(Control.status == ControlStatusEnum.non_compliant).label("non_compliant")
            ).group_by(Control.iso_domain)
        )
        
        by_domain = {}
        for row in domain_result.all():
            domain_total = row.total
            domain_compliant = row.compliant
            by_domain[row.iso_domain] = {
                "total": domain_total,
                "compliant": domain_compliant,
                "partial": row.partial,
                "non_compliant": row.non_compliant,
                "compliance_pct": round((domain_compliant / domain_total * 100), 2) if domain_total > 0 else 0.0
            }
            
        return {
            "total_controls": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": non_compliant,
            "global_compliance_pct": round(global_compliance_pct, 2),
            "by_domain": by_domain
        }
