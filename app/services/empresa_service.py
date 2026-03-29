from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.models.empresa import Empresa
from app.models.control import Control
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate
from app.utils.actividad_controles import get_controls_for_empresa
from app.utils.enums import ControlStatusEnum
from uuid import UUID
from datetime import datetime, timezone


class EmpresaService:

    @staticmethod
    async def _assign_controls(db: AsyncSession, empresa_id: UUID, actividad_economica: str) -> int:
        """Elimina controles existentes de la empresa y genera los que corresponden a su actividad."""
        await db.execute(delete(Control).where(Control.empresa_id == empresa_id))

        controls_data = get_controls_for_empresa(actividad_economica)
        for c in controls_data:
            db.add(Control(
                empresa_id=empresa_id,
                iso_domain=c["iso_domain"],
                iso_control_ref=c["iso_control_ref"],
                name=c["name"],
                description=c["description"],
                status=ControlStatusEnum.non_compliant,
                compliance_pct=0.0,
            ))
        await db.flush()
        return len(controls_data)

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
        await db.flush()  # obtiene el id generado antes del commit

        await EmpresaService._assign_controls(db, db_empresa.id, db_empresa.actividad_economica)

        await db.commit()
        await db.refresh(db_empresa)
        return db_empresa

    @staticmethod
    async def update(db: AsyncSession, empresa_id: UUID, empresa_update: EmpresaUpdate):
        db_empresa = await EmpresaService.get_by_id(db, empresa_id)
        if not db_empresa:
            return None

        update_data = empresa_update.model_dump(exclude_unset=True)
        actividad_changed = (
            "actividad_economica" in update_data
            and update_data["actividad_economica"] != db_empresa.actividad_economica
        )

        for field, value in update_data.items():
            setattr(db_empresa, field, value)
        db_empresa.updated_at = datetime.now(timezone.utc)

        if actividad_changed:
            await EmpresaService._assign_controls(db, empresa_id, db_empresa.actividad_economica)

        await db.commit()
        await db.refresh(db_empresa)
        return db_empresa

    @staticmethod
    async def regenerate_controls(db: AsyncSession, empresa_id: UUID) -> int:
        """Regenera los controles de una empresa existente según su actividad actual."""
        db_empresa = await EmpresaService.get_by_id(db, empresa_id)
        if not db_empresa:
            return -1
        count = await EmpresaService._assign_controls(db, empresa_id, db_empresa.actividad_economica)
        await db.commit()
        return count

    @staticmethod
    async def delete(db: AsyncSession, empresa_id: UUID):
        db_empresa = await EmpresaService.get_by_id(db, empresa_id)
        if not db_empresa:
            return False
        await db.delete(db_empresa)
        await db.commit()
        return True
