from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import os

from app.database import get_db

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


async def _validate_supabase_token(token: str) -> dict:
    """Valida el JWT con Supabase y retorna los datos del usuario.
    NO verifica si existe perfil en la DB — solo autentica."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = response.json()
    return {"user_id": str(data.get("id")), "email": data.get("email")}


async def get_supabase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Solo valida el JWT de Supabase. No requiere perfil en la DB.
    Usar para endpoints de bootstrapping (register-profile)."""
    return await _validate_supabase_token(credentials.credentials)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Valida JWT y verifica que el usuario tenga perfil con rol en la DB."""
    supabase_user = await _validate_supabase_token(credentials.credentials)
    user_id = supabase_user["user_id"]
    email = supabase_user["email"]

    from app.models.user_profile import UserProfile

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin perfil en el sistema. Contacta al administrador.",
        )

    return {
        "user_id": user_id,
        "email": email,
        "role": profile.role.value,
        "empresa_id": str(profile.empresa_id) if profile.empresa_id else None,
    }


def require_role(allowed_roles: list[str]):
    """Dependency factory: solo permite acceso a los roles indicados."""
    async def checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        user = await get_current_user(credentials, db)
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Requiere rol: {', '.join(allowed_roles)}",
            )
        return user
    return checker
