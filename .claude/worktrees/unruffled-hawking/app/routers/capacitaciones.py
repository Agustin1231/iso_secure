from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.auth import get_current_user, require_role
from app.schemas.curso import CursoCreate, CursoUpdate, CursoResponse, CursoWithProgreso, ProgresoUpdate
from app.services import capacitacion_service

router = APIRouter()


@router.get("/", response_model=list[CursoWithProgreso])
async def list_cursos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista todos los cursos con el progreso del usuario autenticado."""
    user_id = UUID(current_user["user_id"])
    return await capacitacion_service.get_all_cursos_with_progreso(db, user_id)


@router.get("/{curso_id}", response_model=CursoWithProgreso)
async def get_curso(
    curso_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    curso = await capacitacion_service.get_curso_by_id(db, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    user_id = UUID(current_user["user_id"])
    progreso = await capacitacion_service.get_progreso(db, curso_id, user_id)
    return {
        "id": curso.id, "titulo": curso.titulo, "descripcion": curso.descripcion,
        "video_url": curso.video_url, "material_texto": curso.material_texto,
        "categoria": curso.categoria, "nivel": curso.nivel.value,
        "created_at": curso.created_at, "progreso": progreso.value,
    }


@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def create_curso(
    data: CursoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    """Crear curso — solo admin."""
    return await capacitacion_service.create_curso(db, data)


@router.put("/{curso_id}", response_model=CursoResponse)
async def update_curso(
    curso_id: UUID,
    data: CursoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    curso = await capacitacion_service.update_curso(db, curso_id, data)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso


@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(
    curso_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    ok = await capacitacion_service.delete_curso(db, curso_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Curso no encontrado")


@router.patch("/{curso_id}/progreso")
async def update_progreso(
    curso_id: UUID,
    data: ProgresoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Actualizar progreso personal del usuario en un curso."""
    user_id = UUID(current_user["user_id"])
    registro = await capacitacion_service.update_progreso(db, curso_id, user_id, data.status)
    return {"curso_id": str(curso_id), "user_id": str(user_id), "status": registro.status.value}
