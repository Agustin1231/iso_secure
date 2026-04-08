from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models.empresa import Empresa
from app.utils.actividad_controles import get_recomendaciones

router = APIRouter()


@router.get("/{empresa_id}")
async def get_implementacion(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "auditor"])),
):
    """
    Retorna los dominios ISO 27001 recomendados para la empresa según su actividad económica.
    """
    result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
    empresa = result.scalar_one_or_none()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    recomendaciones, sector = get_recomendaciones(empresa.actividad_economica)

    return {
        "empresa_id": str(empresa_id),
        "empresa_nombre": empresa.nombre,
        "actividad_economica": empresa.actividad_economica,
        "sector_detectado": sector,
        "total_recomendaciones": len(recomendaciones),
        "recomendaciones": recomendaciones,
    }
