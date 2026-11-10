"""The ONE place where configuration is read (Playbook CFG-01).

Why one place?  If every file reads the environment on its own, nobody knows which
settings exist.  Here every setting has a name, a type, and a default (or is required).
A missing or invalid required value stops the app at start-up with a clear message
(CFG-02), which is better than failing at 2 a.m.
"""

from functools import lru_cache

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings. Values come from environment variables or from `app.env`."""

    # `app.env` is for the app only. Never commit it (CFG-04). Copy `app.env.example`.
    model_config = SettingsConfigDict(env_file="app.env", env_prefix="", extra="ignore")

    # --- application
    app_environment: str = "development"  # development | production
    app_base_path: str = ""  # set when the app sits behind a proxy prefix (ARC-12)
    app_timezone: str = "UTC"

    # --- database (a least-privilege role, not the admin: DB-02)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "example"
    postgres_user: str = "app_user"
    postgres_password: SecretStr = SecretStr("")  # SecretStr hides the value if printed (CFG-09)

    # --- language model (provider-agnostic: switch provider by changing these three)
    llm_base_url: str = ""
    llm_model: str = ""
    llm_api_key: SecretStr = SecretStr("")
    llm_timeout_seconds: float = 30.0

    @property
    def docs_enabled(self) -> bool:
        """Interactive API docs only in development (ARC-09)."""
        return self.app_environment == "development"

    @model_validator(mode="after")
    def validate_production_settings(self) -> Settings:
        """Require database and LLM credentials in production only."""
        if self.app_environment == "production":
            missing = []
            if not self.postgres_password.get_secret_value():
                missing.append("POSTGRES_PASSWORD")
            if not self.llm_base_url:
                missing.append("LLM_BASE_URL")
            if not self.llm_model:
                missing.append("LLM_MODEL")
            if not self.llm_api_key.get_secret_value():
                missing.append("LLM_API_KEY")

            if missing:
                raise ValueError("Missing required production settings: " + ", ".join(missing))
        return self


@lru_cache
def get_settings() -> Settings:
    """Build the settings once and reuse them."""
    return Settings()
