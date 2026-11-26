"""Registration and authentication endpoints."""

import hashlib
import logging
import secrets

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from app.config import get_settings
from app.services.password_security import hash_password, verify_password


def require_csrf_header(request: Request) -> None:
    """Reject requests without the required CSRF header."""
    if request.headers.get("X-CSRF-Protection") != "1":
        raise HTTPException(
            status_code=403,
            detail="CSRF protection header required.",
        )


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    dependencies=[Depends(require_csrf_header)],
)
logger = logging.getLogger(__name__)
DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=15, max_length=1024)


class RegisterResponse(BaseModel):
    message: str


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register_user(data: RegisterRequest) -> RegisterResponse:
    """Register a new user with the default reader role."""
    settings = get_settings()

    try:
        password_hash = hash_password(data.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None

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
            conn.execute(
                """
                WITH new_user AS (
                    INSERT INTO auth_users (email, password_hash)
                    VALUES (%s, %s)
                    RETURNING id
                )
                INSERT INTO auth_audit_events (user_id, event_type)
                SELECT id, 'registration_success' FROM new_user
                """,
                (data.email.lower(), password_hash),
            )

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Unable to register account.",
        ) from None

    except psycopg.Error:
        logger.warning("Registration database operation failed")
        raise HTTPException(
            status_code=503,
            detail="Registration temporarily unavailable.",
        ) from None

    return RegisterResponse(message="Registration successful")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class LoginResponse(BaseModel):
    message: str


@router.post("/login", response_model=LoginResponse)
def login_user(data: LoginRequest, request: Request) -> LoginResponse:
    """Authenticate a user and create a server-side session."""
    settings = get_settings()
    email = data.email.lower()
    identifier = hashlib.sha256(email.encode()).hexdigest()
    session_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(session_token.encode()).hexdigest()
    authenticated = False

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
            conn.execute(
                """
                INSERT INTO auth_login_attempts (identifier_hash)
                VALUES (%s)
                ON CONFLICT DO NOTHING
                """,
                (identifier,),
            )

            attempt = conn.execute(
                """
                SELECT failed_attempts, locked_until > now(),
                       CEIL(EXTRACT(EPOCH FROM (locked_until - now())))
                FROM auth_login_attempts
                WHERE identifier_hash = %s
                FOR UPDATE
                """,
                (identifier,),
            ).fetchone()

            if attempt and attempt[1]:
                raise HTTPException(
                    status_code=429,
                    detail="Too many login attempts. Try again later.",
                    headers={"Retry-After": str(max(1, int(attempt[2])))},
                )

            user = conn.execute(
                """
                SELECT id, password_hash FROM auth_users
                WHERE email = %s
                """,
                (email,),
            ).fetchone()

            valid = verify_password(data.password, user[1] if user else DUMMY_HASH)

            if user and valid:
                conn.execute(
                    """
                    INSERT INTO auth_sessions
                    (token_hash, user_id, expires_at)
                    VALUES (%s, %s, now() + interval '1 hour')
                    """,
                    (token_hash, user[0]),
                )

                conn.execute(
                    """
                    DELETE FROM auth_login_attempts
                    WHERE identifier_hash = %s
                    """,
                    (identifier,),
                )

                conn.execute(
                    """
                    INSERT INTO auth_audit_events (user_id, event_type)
                    VALUES (%s, 'login_success')
                    """,
                    (user[0],),
                )
                authenticated = True
            else:
                conn.execute(
                    """
                    UPDATE auth_login_attempts
                    SET failed_attempts = CASE
                        WHEN updated_at < now() - interval '15 minutes'
                        THEN 1 ELSE failed_attempts + 1 END,
                        locked_until = CASE
                        WHEN updated_at >= now() - interval '15 minutes'
                        AND failed_attempts >= 4
                        THEN now() + interval '15 minutes'
                        ELSE NULL END,
                        updated_at = now()
                    WHERE identifier_hash = %s
                    """,
                    (identifier,),
                )

                conn.execute(
                    """
                    INSERT INTO auth_audit_events (user_id, event_type)
                    VALUES (%s, 'login_failure')
                    """,
                    (user[0] if user else None,),
                )

    except psycopg.Error:
        logger.warning("Login database operation failed")
        raise HTTPException(
            status_code=503,
            detail="Login temporarily unavailable.",
        ) from None

    if not authenticated:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials.",
        )

    request.session.clear()
    request.session["auth_token"] = session_token
    return LoginResponse(message="Login successful")


@router.post("/logout")
def logout_user(request: Request) -> dict[str, str]:
    """Invalidate the server-side session and clear the cookie."""
    token = request.session.get("auth_token")

    if token:
        settings = get_settings()
        token_hash = hashlib.sha256(token.encode()).hexdigest()

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
                conn.execute(
                    """
                    WITH removed_session AS (
                        DELETE FROM auth_sessions
                        WHERE token_hash = %s
                        RETURNING user_id
                    )
                    INSERT INTO auth_audit_events (user_id, event_type)
                    SELECT user_id, 'logout_success'
                    FROM removed_session
                    """,
                    (token_hash,),
                )

        except psycopg.Error:
            logger.warning("Logout database operation failed")
            raise HTTPException(
                status_code=503,
                detail="Logout temporarily unavailable.",
            ) from None

    request.session.clear()
    return {"message": "Logout successful"}
