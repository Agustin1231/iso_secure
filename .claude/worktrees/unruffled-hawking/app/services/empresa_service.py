from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate
from uuid import UUID
from datetime import datetime, timezone


class EmpresaService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 50, actividad: str = None):
        query = select(Empresa).order_by(Empresa.nombre.asc())
        if actividad:
            query = query.where(Empresa.actividad_economica.ilike(f"%{actividad}%"))

        total_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(total_query)).scalar()

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        serialized = []
        for e in items:
            serialized.append({
                "id": str(e.id),
                "nombre": e.nombre,
                "tipo_empresa": e.tipo_empresa,
                "actividad_economica": e.actividad_economica,
                "representante_legal": e.representante_legal,
                "email": e.email,
                "telefono": e.telefono,
                "nit": e.nit,
                "direccion": e.direccion,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "updated_at": e.updated_at.isoformat() if e.updated_at else None,
            })

        return {"total": total, "items": serialized}

    @staticmethod
    async def get_by_id(db: AsyncSession, empresa_id: UUID):
        result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, empresa_in: EmpresaCreate):
        db_empresa = Empresa(**empresa_in.model_dump())
        db.add(db_empresa)
        await db.commit()
        await db.refresh(db_empresa)
        return db_empresa

    @staticmethod
    async def update(db: AsyncSession, empresa_id: UUID, empresa_update: EmpresaUpdate):
        db_empresa = await EmpresaService.get_by_id(db, empresa_id)
        if not db_empresa:
            return None
        update_data = empresa_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_empresa, field, value)
        db_empresa.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_empresa)
        return db_empresa

    @staticmethod
    async def delete(db: AsyncSession, empresa_id: UUID):
        db_empresa = await EmpresaService.get_by_id(db, empresa_id)
        if not db_empresa:
            return False
        await db.delete(db_empresa)
        await db.commit()
        return True
