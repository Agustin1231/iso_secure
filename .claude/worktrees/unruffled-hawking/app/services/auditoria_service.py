from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.auditoria_item import AuditoriaItem
from app.models.control import Control
from app.schemas.auditoria import AuditoriaItemCreate, AuditoriaItemUpdate
from app.utils.enums import AuditoriaStatusEnum


async def get_items_by_empresa(db: AsyncSession, empresa_id: UUID) -> list[AuditoriaItem]:
    result = await db.execute(
        select(AuditoriaItem).where(AuditoriaItem.empresa_id == empresa_id).order_by(AuditoriaItem.created_at)
    )
    return result.scalars().all()


async def get_item_by_id(db: AsyncSession, item_id: UUID) -> AuditoriaItem | None:
    result = await db.execute(select(AuditoriaItem).where(AuditoriaItem.id == item_id))
    return result.scalar_one_or_none()


async def create_item(db: AsyncSession, data: AuditoriaItemCreate, auditor_id: UUID) -> AuditoriaItem:
    item = AuditoriaItem(**data.model_dump(), auditor_id=auditor_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_item(db: AsyncSession, item_id: UUID, data: AuditoriaItemUpdate, auditor_id: UUID) -> AuditoriaItem | None:
    item = await get_item_by_id(db, item_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.auditor_id = auditor_id
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item_id: UUID) -> bool:
    item = await get_item_by_id(db, item_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True


async def generate_items_from_controls(db: AsyncSession, empresa_id: UUID, auditor_id: UUID) -> list[AuditoriaItem]:
    """Genera items de auditoría a partir de los controles existentes en la DB."""
    result = await db.execute(select(Control).order_by(Control.iso_domain, Control.iso_control_ref))
    controls = result.scalars().all()

    existing = await get_items_by_empresa(db, empresa_id)
    existing_refs = {item.iso_control_ref for item in existing if item.iso_control_ref}

    new_items = []
    for ctrl in controls:
        if ctrl.iso_control_ref and ctrl.iso_control_ref in existing_refs:
            continue
        item = AuditoriaItem(
            empresa_id=empresa_id,
            iso_control_ref=ctrl.iso_control_ref,
            control_name=ctrl.name,
            activity_desc=ctrl.description,
            status=AuditoriaStatusEnum.pendiente,
            auditor_id=auditor_id,
        )
        db.add(item)
        new_items.append(item)

    await db.commit()
    for item in new_items:
        await db.refresh(item)
    return new_items


async def get_resumen(db: AsyncSession, empresa_id: UUID) -> dict:
    items = await get_items_by_empresa(db, empresa_id)
    total = len(items)
    by_status = {"pendiente": 0, "en_proceso": 0, "completado": 0}
    for item in items:
        by_status[item.status.value] += 1
    pct = round((by_status["completado"] / total * 100), 1) if total > 0 else 0
    return {"total": total, "by_status": by_status, "completion_pct": pct}
