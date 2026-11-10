"""What "ready" means for this service.

Each check returns a short problem text, or nothing when all is well.
"""

import logging

import psycopg

from app.config import get_settings

logger = logging.getLogger(__name__)


def check_dependencies() -> list[str]:
    """Check that required dependencies are reachable."""
    settings = get_settings()

    try:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password.get_secret_value(),
            connect_timeout=3,
        ) as connection:
            connection.execute("SELECT 1")
    except psycopg.Error:
        logger.warning("database readiness check failed")
        return ["database unavailable"]

    return []
