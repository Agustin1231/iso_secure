from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth import get_current_user, get_supabase_user, require_role
from app.models.user_profile import UserProfile
from app.utils.enums import UserRoleEnum
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import uuid

router = APIRouter()


class UserProfileResponse(BaseModel):
    user_id: str
    email: Optional[str]
    role: str
    empresa_id: Optional[str]


class RoleUpdate(BaseModel):
    role: UserRoleEnum
    empresa_id: Optional[UUID] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado"""
    return current_user


@router.get("/users", response_model=dict)
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    """Listar todos los perfiles de usuario (solo admin)"""
    result = await db.execute(select(UserProfile).order_by(UserProfile.created_at.desc()))
    profiles = result.scalars().all()
    return {
        "total": len(profiles),
        "items": [
            {
                "id": str(p.id),
                "user_id": str(p.user_id),
                "email": p.email,
                "role": p.role.value,
                "empresa_id": str(p.empresa_id) if p.empresa_id else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in profiles
        ],
    }


@router.put("/users/{user_id}/role", response_model=UserProfileResponse)
async def update_user_role(
    user_id: str,
    role_update: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    """Actualizar rol y empresa de un usuario (solo admin)"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == uuid.UUID(user_id))
    )
    profile = result.scalar_one_or_none()

    if not profile:
        # Create profile if it doesn't exist yet
        profile = UserProfile(
            user_id=uuid.UUID(user_id),
            role=role_update.role,
            empresa_id=role_update.empresa_id,
        )
        db.add(profile)
    else:
        profile.role = role_update.role
        if role_update.empresa_id is not None:
            profile.empresa_id = role_update.empresa_id

    await db.commit()
    await db.refresh(profile)

    return {
        "user_id": str(profile.user_id),
        "email": profile.email,
        "role": profile.role.value,
        "empresa_id": str(profile.empresa_id) if profile.empresa_id else None,
    }


@router.post("/register-profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_supabase_user),  # solo valida JWT, sin requerir perfil previo
):
    """
    Crea el perfil del usuario autenticado si no existe.
    Rol por defecto: analista.
    """
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == uuid.UUID(current_user["user_id"]))
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {
            "user_id": str(existing.user_id),
            "email": existing.email,
            "role": existing.role.value,
            "empresa_id": str(existing.empresa_id) if existing.empresa_id else None,
        }

    profile = UserProfile(
        user_id=uuid.UUID(current_user["user_id"]),
        email=current_user.get("email"),
        role=UserRoleEnum.analista,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return {
        "user_id": str(profile.user_id),
        "email": profile.email,
        "role": profile.role.value,
        "empresa_id": None,
    }
