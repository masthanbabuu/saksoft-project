"""Centralized session validation and role-based access control."""

import hashlib
from dataclasses import dataclass
from typing import Annotated

import psycopg
from fastapi import Depends, HTTPException, Request

from app.config import get_settings


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    role: str


def get_current_user(request: Request) -> AuthenticatedUser:
    """Validate the server-side session."""
    token = request.session.get("auth_token")

    if not isinstance(token, str) or not token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    settings = get_settings()

    try:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password.get_secret_value(),
            connect_timeout=3,
            options="-c statement_timeout=5000",
        ) as conn:
            user = conn.execute(
                """
                SELECT u.id, u.role
                FROM auth_sessions s
                JOIN auth_users u ON u.id = s.user_id
                WHERE s.token_hash = %s
                AND s.expires_at > now()
                """,
                (token_hash,),
            ).fetchone()

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Authentication temporarily unavailable.",
        ) from None

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return AuthenticatedUser(id=user[0], role=user[1])


def require_reader(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> AuthenticatedUser:
    """Allow readers and administrators."""
    if user.role not in {"reader", "admin"}:
        raise HTTPException(status_code=403, detail="Access denied.")
    return user


def require_admin(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> AuthenticatedUser:
    """Allow administrators only."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
    return user
