"""Módulo de administración de Roles y Permisos (RBAC).

- Los **super administradores** crean y administran permisos y roles.
- Los **administradores de cada empresa** asignan y quitan roles a los
  usuarios que pertenecen a su misma empresa.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.auth import require_role
from app.services.rbac_service import RBACService
from app.models.user_profile import UserProfile
from app.models.role import Role
from app.schemas.rbac import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    UserRoleAssign, UserRoleResponse,
)

router = APIRouter()

# Solo super administradores administran el catálogo de permisos/roles.
require_super_admin = require_role(["super_admin"])
# Administradores de empresa (super_admin pasa siempre por el bypass de require_role).
require_admin = require_role(["admin"])


async def _assert_can_manage_user(current_user: dict, target: UserProfile) -> None:
    """Valida que el usuario actual pueda gestionar roles del usuario objetivo.

    - super_admin: puede gestionar cualquier usuario.
    - admin: solo usuarios de su misma empresa.
    """
    if current_user["role"] == "super_admin":
        return
    actor_empresa = current_user.get("empresa_id")
    target_empresa = str(target.empresa_id) if target.empresa_id else None
    if not actor_empresa or actor_empresa != target_empresa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes gestionar roles de usuarios de tu empresa.",
        )


def _user_role_payload(user_role) -> dict:
    return {
        "id": user_role.id,
        "role_id": user_role.role_id,
        "role_nombre": user_role.role.nombre if user_role.role else None,
        "user_profile_id": user_role.user_profile_id,
        "empresa_id": user_role.empresa_id,
        "assigned_by": user_role.assigned_by,
        "created_at": user_role.created_at,
    }


# ─── Permisos ─────────────────────────────────────────────────────────────────
@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Lista el catálogo de permisos. Lo consultan admin y super_admin."""
    return await RBACService.list_permissions(db)


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Crea un permiso (solo super administradores)."""
    perm = await RBACService.create_permission(db, data)
    if perm is None:
        raise HTTPException(status_code=409, detail=f"Ya existe un permiso con el código '{data.codigo}'.")
    return perm


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: UUID,
    data: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Actualiza un permiso (solo super administradores)."""
    perm = await RBACService.update_permission(db, permission_id, data)
    if perm is None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado.")
    return perm


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Elimina un permiso (solo super administradores)."""
    if not await RBACService.delete_permission(db, permission_id):
        raise HTTPException(status_code=404, detail="Permiso no encontrado.")


# ─── Roles ────────────────────────────────────────────────────────────────────
@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Lista los roles con sus permisos. Lo consultan admin y super_admin
    (el admin los necesita para asignarlos a sus usuarios)."""
    return await RBACService.list_roles(db)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Crea un rol y le asocia permisos (solo super administradores)."""
    role = await RBACService.create_role(db, data)
    if role is None:
        raise HTTPException(status_code=409, detail=f"Ya existe un rol con el nombre '{data.nombre}'.")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Actualiza un rol y sus permisos (solo super administradores)."""
    role = await RBACService.update_role(db, role_id, data)
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Elimina un rol (solo super administradores). Los roles de sistema
    están protegidos contra eliminación."""
    outcome = await RBACService.delete_role(db, role_id)
    if outcome == "not_found":
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    if outcome == "protected":
        raise HTTPException(status_code=409, detail="No se puede eliminar un rol de sistema.")


# ─── Asignación de roles a usuarios ───────────────────────────────────────────
@router.get("/users/{user_profile_id}/roles", response_model=list[UserRoleResponse])
async def list_user_roles(
    user_profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Lista los roles asignados a un usuario."""
    profile = await db.get(UserProfile, user_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    await _assert_can_manage_user(current_user, profile)
    items = await RBACService.list_user_roles(db, user_profile_id)
    return [_user_role_payload(i) for i in items]


@router.post("/users/{user_profile_id}/roles", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_user_role(
    user_profile_id: UUID,
    body: UserRoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Asigna un rol a un usuario de la empresa (administradores de empresa)."""
    profile = await db.get(UserProfile, user_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    await _assert_can_manage_user(current_user, profile)

    role = await db.get(Role, body.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")

    user_role = await RBACService.assign_role(
        db,
        user_profile_id=user_profile_id,
        role_id=body.role_id,
        empresa_id=profile.empresa_id,
        assigned_by=UUID(current_user["user_id"]),
    )
    return _user_role_payload(user_role)


@router.delete("/users/{user_profile_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_role(
    user_profile_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Quita un rol a un usuario de la empresa (administradores de empresa)."""
    profile = await db.get(UserProfile, user_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    await _assert_can_manage_user(current_user, profile)

    if not await RBACService.remove_role(db, user_profile_id, role_id):
        raise HTTPException(status_code=404, detail="El usuario no tiene ese rol asignado.")
