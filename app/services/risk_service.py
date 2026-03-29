from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from app.models.risk import RiskLevel
from app.schemas.risk import RiskCreate
from app.utils.enums import RiskLevelEnum
from datetime import datetime, timezone, timedelta
from uuid import UUID

class RiskService:
    @staticmethod
    def calculate_risk_level(probability: int, impact: int) -> tuple[int, str]:
        score = probability * impact
        if score <= 4:
            level = RiskLevelEnum.low
        elif score <= 9:
            level = RiskLevelEnum.medium
        elif score <= 16:
            level = RiskLevelEnum.high
        else:
            level = RiskLevelEnum.critical
        return score, level

    @staticmethod
    async def create(db: AsyncSession, risk_in: RiskCreate):
        score, level = RiskService.calculate_risk_level(risk_in.probability, risk_in.impact)
        db_risk = RiskLevel(
            domain=risk_in.domain,
            probability=risk_in.probability,
            impact=risk_in.impact,
            score=score,
            level=level,
            notes=risk_in.notes
        )
        db.add(db_risk)
        await db.commit()
        await db.refresh(db_risk)
        return db_risk

    @staticmethod
    async def get_history(db: AsyncSession, days: int = 90, domain: str = None, skip: int = 0, limit: int = 50, empresa_id: str = None):
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(RiskLevel).where(RiskLevel.recorded_at >= since_date).order_by(RiskLevel.recorded_at.desc())

        if empresa_id:
            query = query.where(RiskLevel.empresa_id == empresa_id)
        if domain:
            query = query.where(RiskLevel.domain == domain)
            
        total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return {"total": total, "items": items}

    @staticmethod
    async def get_by_domain(db: AsyncSession, empresa_id: str = None):
        empresa_filter = (RiskLevel.empresa_id == empresa_id,) if empresa_id else ()
        # Subquery to get max recorded_at for each domain
        subq = (
            select(RiskLevel.domain, func.max(RiskLevel.recorded_at).label("max_recorded"))
            .where(*empresa_filter)
            .group_by(RiskLevel.domain)
            .subquery()
        )
        
        # Join with the full table to get the full record
        query = (
            select(RiskLevel)
            .join(subq, and_(RiskLevel.domain == subq.c.domain, RiskLevel.recorded_at == subq.c.max_recorded))
            .order_by(desc(RiskLevel.score))
        )
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return {"domains": items, "total": len(items)}

    @staticmethod
    async def get_current_stats(db: AsyncSession, empresa_id: str = None):
        current_risks = await RiskService.get_by_domain(db, empresa_id=empresa_id)
        items = current_risks["domains"]
        
        if not items:
            return {
                "global_score": 0.0,
                "global_level": "low",
                "total_domains": 0,
                "by_level": {"low": 0, "medium": 0, "high": 0, "critical": 0},
                "highest_risk_domain": None,
                "recorded_at": datetime.now(timezone.utc)
            }
            
        scores = [r.score for r in items]
        global_score = sum(scores) / len(scores)
        _, global_level = RiskService.calculate_risk_level(1, global_score / 5 if global_score > 0 else 0)
        # Recalculate level properly based on the score average directly
        # If score 1-4=low, 5-9=medium, 10-16=high, 17-25=critical
        if global_score <= 4:
            global_level = RiskLevelEnum.low
        elif global_score <= 9:
            global_level = RiskLevelEnum.medium
        elif global_score <= 16:
            global_level = RiskLevelEnum.high
        else:
            global_level = RiskLevelEnum.critical

        by_level = {
            RiskLevelEnum.low: 0, 
            RiskLevelEnum.medium: 0, 
            RiskLevelEnum.high: 0, 
            RiskLevelEnum.critical: 0
        }
        max_score = -1
        highest_domain = None
        max_recorded = items[0].recorded_at
        
        for r in items:
            level_str = getattr(r.level, 'value', r.level)
            by_level[level_str] = by_level.get(level_str, 0) + 1
            if r.score > max_score:
                max_score = r.score
                highest_domain = r.domain
            if r.recorded_at > max_recorded:
                max_recorded = r.recorded_at
                
        return {
            "global_score": round(global_score, 1),
            "global_level": getattr(global_level, 'value', global_level),
            "total_domains": len(items),
            "by_level": by_level,
            "highest_risk_domain": highest_domain,
            "recorded_at": max_recorded
        }
