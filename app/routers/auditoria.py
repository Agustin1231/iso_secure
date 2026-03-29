from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.auth import get_current_user, require_role
from app.schemas.auditoria import AuditoriaItemCreate, AuditoriaItemUpdate, AuditoriaItemResponse
from app.services import auditoria_service

router = APIRouter()


@router.get("/empresa/{empresa_id}", response_model=list[AuditoriaItemResponse])
async def list_items(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    """Lista todos los items de auditoría de una empresa."""
    return await auditoria_service.get_items_by_empresa(db, empresa_id)


@router.get("/empresa/{empresa_id}/resumen")
async def resumen(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    """Resumen de progreso de auditoría para una empresa."""
    return await auditoria_service.get_resumen(db, empresa_id)


@router.post("/empresa/{empresa_id}/generar", response_model=list[AuditoriaItemResponse], status_code=status.HTTP_201_CREATED)
async def generar_items(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    """Genera items de auditoría a partir de los controles existentes (no duplica)."""
    auditor_id = UUID(current_user["user_id"])
    return await auditoria_service.generate_items_from_controls(db, empresa_id, auditor_id)


@router.post("/", response_model=AuditoriaItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: AuditoriaItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    auditor_id = UUID(current_user["user_id"])
    return await auditoria_service.create_item(db, data, auditor_id)


@router.put("/{item_id}", response_model=AuditoriaItemResponse)
async def update_item(
    item_id: UUID,
    data: AuditoriaItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    auditor_id = UUID(current_user["user_id"])
    item = await auditoria_service.update_item(db, item_id, data, auditor_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    ok = await auditoria_service.delete_item(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item no encontrado")
