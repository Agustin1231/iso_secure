from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.curso import Curso
from app.models.curso_progreso import CursoProgreso
from app.schemas.curso import CursoCreate, CursoUpdate
from app.utils.enums import ProgresoEnum


async def get_all_cursos(db: AsyncSession) -> list[Curso]:
    result = await db.execute(select(Curso).order_by(Curso.created_at.desc()))
    return result.scalars().all()


async def get_curso_by_id(db: AsyncSession, curso_id: UUID) -> Curso | None:
    result = await db.execute(select(Curso).where(Curso.id == curso_id))
    return result.scalar_one_or_none()


async def create_curso(db: AsyncSession, data: CursoCreate) -> Curso:
    curso = Curso(**data.model_dump())
    db.add(curso)
    await db.commit()
    await db.refresh(curso)
    return curso


async def update_curso(db: AsyncSession, curso_id: UUID, data: CursoUpdate) -> Curso | None:
    curso = await get_curso_by_id(db, curso_id)
    if not curso:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(curso, field, value)
    await db.commit()
    await db.refresh(curso)
    return curso


async def delete_curso(db: AsyncSession, curso_id: UUID) -> bool:
    curso = await get_curso_by_id(db, curso_id)
    if not curso:
        return False
    await db.delete(curso)
    await db.commit()
    return True


async def get_progreso(db: AsyncSession, curso_id: UUID, user_id: UUID) -> ProgresoEnum:
    result = await db.execute(
        select(CursoProgreso).where(
            CursoProgreso.curso_id == curso_id,
            CursoProgreso.user_id == user_id,
        )
    )
    registro = result.scalar_one_or_none()
    return registro.status if registro else ProgresoEnum.pendiente


async def update_progreso(db: AsyncSession, curso_id: UUID, user_id: UUID, status: ProgresoEnum) -> CursoProgreso:
    result = await db.execute(
        select(CursoProgreso).where(
            CursoProgreso.curso_id == curso_id,
            CursoProgreso.user_id == user_id,
        )
    )
    registro = result.scalar_one_or_none()
    if registro:
        registro.status = status
    else:
        registro = CursoProgreso(curso_id=curso_id, user_id=user_id, status=status)
        db.add(registro)
    await db.commit()
    await db.refresh(registro)
    return registro


async def get_all_cursos_with_progreso(db: AsyncSession, user_id: UUID) -> list[dict]:
    cursos = await get_all_cursos(db)
    result = await db.execute(
        select(CursoProgreso).where(CursoProgreso.user_id == user_id)
    )
    progresos = {p.curso_id: p.status.value for p in result.scalars().all()}
    return [
        {**{c: getattr(curso, c) for c in ["id", "titulo", "descripcion", "video_url", "material_texto", "categoria", "nivel", "created_at"]},
         "nivel": curso.nivel.value,
         "progreso": progresos.get(curso.id, "pendiente")}
        for curso in cursos
    ]
