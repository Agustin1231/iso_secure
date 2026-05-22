"""Capa de lógica de negocio para la gestión de permisos, roles y
asignación de roles a usuarios (RBAC dinámico)."""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.rbac import (
    PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate,
)


class RBACService:

    # ── Permisos (solo super administradores) ─────────────────────────────────
    @staticmethod
    async def list_permissions(db: AsyncSession):
        result = await db.execute(
            select(Permission).order_by(Permission.modulo, Permission.codigo)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_permission(db: AsyncSession, data: PermissionCreate):
        existing = await db.execute(
            select(Permission).where(Permission.codigo == data.codigo)
        )
        if existing.scalar_one_or_none():
            return None  # código duplicado
        perm = Permission(**data.model_dump())
        db.add(perm)
        await db.commit()
        await db.refresh(perm)
        return perm

    @staticmethod
    async def update_permission(db: AsyncSession, permission_id: UUID, data: PermissionUpdate):
        perm = await db.get(Permission, permission_id)
        if not perm:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(perm, field, value)
        await db.commit()
        await db.refresh(perm)
        return perm

    @staticmethod
    async def delete_permission(db: AsyncSession, permission_id: UUID) -> bool:
        perm = await db.get(Permission, permission_id)
        if not perm:
            return False
        await db.delete(perm)
        await db.commit()
        return True

    # ── Roles (solo super administradores) ────────────────────────────────────
    @staticmethod
    async def list_roles(db: AsyncSession):
        result = await db.execute(select(Role).order_by(Role.nombre))
        return list(result.scalars().all())

    @staticmethod
    async def get_role(db: AsyncSession, role_id: UUID):
        result = await db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def _load_permissions(db: AsyncSession, ids: list[UUID]):
        if not ids:
            return []
        result = await db.execute(select(Permission).where(Permission.id.in_(ids)))
        return list(result.scalars().all())

    @staticmethod
    async def create_role(db: AsyncSession, data: RoleCreate):
        existing = await db.execute(select(Role).where(Role.nombre == data.nombre))
        if existing.scalar_one_or_none():
            return None  # nombre duplicado
        role = Role(nombre=data.nombre, descripcion=data.descripcion, es_sistema=False)
        role.permissions = await RBACService._load_permissions(db, data.permission_ids)
        db.add(role)
        await db.commit()
        return await RBACService.get_role(db, role.id)

    @staticmethod
    async def update_role(db: AsyncSession, role_id: UUID, data: RoleUpdate):
        role = await db.get(Role, role_id)
        if not role:
            return None
        if data.nombre is not None:
            role.nombre = data.nombre
        if data.descripcion is not None:
            role.descripcion = data.descripcion
        if data.permission_ids is not None:
            role.permissions = await RBACService._load_permissions(db, data.permission_ids)
        await db.commit()
        return await RBACService.get_role(db, role_id)

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: UUID) -> str:
        role = await db.get(Role, role_id)
        if not role:
            return "not_found"
        if role.es_sistema:
            return "protected"
        await db.delete(role)
        await db.commit()
        return "ok"

    # ── Asignación de roles a usuarios (administradores de empresa) ───────────
    @staticmethod
    async def list_user_roles(db: AsyncSession, user_profile_id: UUID):
        result = await db.execute(
            select(UserRole)
            .where(UserRole.user_profile_id == user_profile_id)
            .order_by(UserRole.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def assign_role(
        db: AsyncSession,
        user_profile_id: UUID,
        role_id: UUID,
        empresa_id: UUID | None,
        assigned_by: UUID | None,
    ):
        existing = await db.execute(
            select(UserRole).where(
                UserRole.user_profile_id == user_profile_id,
                UserRole.role_id == role_id,
            )
        )
        current = existing.scalar_one_or_none()
        if current:
            return current  # ya asignado — idempotente
        user_role = UserRole(
            user_profile_id=user_profile_id,
            role_id=role_id,
            empresa_id=empresa_id,
            assigned_by=assigned_by,
        )
        db.add(user_role)
        await db.commit()
        result = await db.execute(
            select(UserRole).where(UserRole.id == user_role.id)
        )
        return result.scalar_one()

    @staticmethod
    async def remove_role(db: AsyncSession, user_profile_id: UUID, role_id: UUID) -> bool:
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_profile_id == user_profile_id,
                UserRole.role_id == role_id,
            )
        )
        user_role = result.scalar_one_or_none()
        if not user_role:
            return False
        await db.delete(user_role)
        await db.commit()
        return True
