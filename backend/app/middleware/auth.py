"""
Auth middleware — Supabase JWT verification.

Usage in a router:
    from app.middleware.auth import get_current_user

    @router.get("/feed")
    async def get_feed(current_user = Depends(get_current_user)):
        ...

Dev mode:
    Set SKIP_AUTH=true in .env to bypass JWT checks entirely.
    In this mode, get_current_user returns a dummy user dict so other team
    members can call the API without Supabase keys configured.
"""

from __future__ import annotations

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

_bearer = HTTPBearer(auto_error=False)

# Cache for Supabase JWKS (public keys used to verify JWTs)
_jwks_cache: dict | None = None


async def _get_supabase_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """
    FastAPI dependency.

    Returns a dict with at minimum {"sub": <user_uuid>} on success.
    Raises HTTP 401 if auth fails (unless SKIP_AUTH=true).
    """
    # ---------------------------------------------------------- dev bypass --
    if settings.skip_auth:
        # Return a dummy user so routes still work without real auth
        return {"sub": "00000000-0000-0000-0000-000000000001", "email": "dev@local"}

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        if settings.auth_provider == "supabase":
            payload = await _verify_supabase_jwt(token)
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Auth provider '{settings.auth_provider}' not yet implemented.",
            )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


async def _verify_supabase_jwt(token: str) -> dict:
    """
    Verify a Supabase-issued JWT using the project's public JWKS.
    Returns the decoded payload dict.
    """
    jwks = await _get_supabase_jwks()

    # Decode header to find the key ID (kid)
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    # Find the matching public key
    public_key = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            public_key = key
            break

    if public_key is None:
        raise JWTError("No matching public key found in JWKS.")

    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="authenticated",
    )
    return payload
