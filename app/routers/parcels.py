"""Parcel endpoints with object-level authorization."""

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.services.auth_security import AuthenticatedUser, require_reader

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.get("/{parcel_id}")
def get_parcel(
    parcel_id: int,
    user: Annotated[AuthenticatedUser, Depends(require_reader)],
) -> dict[str, int | str]:
    """Return a parcel only when the user has permission."""
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
            parcel = conn.execute(
                """
                SELECT id, name, status
                FROM parcels
                WHERE id = %s
                AND (owner_user_id = %s OR %s = 'admin')
                """,
                (parcel_id, user.id, user.role),
            ).fetchone()

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Parcel service temporarily unavailable.",
        ) from None

    if parcel is None:
        raise HTTPException(status_code=404, detail="Parcel not found.")

    return {
        "id": parcel[0],
        "name": parcel[1],
        "status": parcel[2],
    }
