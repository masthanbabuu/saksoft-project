"""Application entry point: builds the FastAPI app.

Reading order for a new engineer:  main.py -> routers/ -> services/ -> models/.
Routers are thin (they only translate HTTP), services hold the logic, models describe data
(Playbook ARC-01).
"""

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.logging_config import request_id_var, setup_logging
from app.routers import ask, auth, health, knowledge, parcels, uploads
from app.security.rate_limit import RateLimitMiddleware
from app.security.request_limits import RequestSizeLimitMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build the app. A function (not a global) makes it easy to test."""
    settings = get_settings()
    setup_logging()

    app = FastAPI(
        title="FDE service",
        # Interactive docs are handy in development and off elsewhere (ARC-09).
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        root_path=settings.app_base_path,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key.get_secret_value(),
        same_site="lax",
        max_age=3600,
        https_only=settings.app_environment == "production",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    )

    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_bytes=settings.max_request_bytes,
    )

    app.add_middleware(
        RateLimitMiddleware,
        limit=settings.rate_limit_requests,
        window=settings.rate_limit_window_seconds,
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Give every request an ID, log with it, and return it to the caller (LOG-03)."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("unhandled error")
                response = JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "internal_error",
                            "message": "Something went wrong.",
                            "request_id": request_id,
                        }
                    },
                )
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Return validation errors in the standard safe error format."""
        request_id = request_id_var.get()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        """One error format and no internals in the response (ARC-03, SEC-13)."""
        logger.error("unhandled error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Something went wrong.",
                    "request_id": request_id_var.get(),
                }
            },
        )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(ask.router)
    app.include_router(knowledge.router)
    app.include_router(parcels.router)
    app.include_router(uploads.router)
    return app


app = create_app()
