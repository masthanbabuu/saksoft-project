"""Configuration tests: secrets must never show up when settings are printed (CFG-09)."""

from pydantic import SecretStr

from app.config import Settings


def test_settings_repr_hides_secret_values():
    settings = Settings(
        postgres_password=SecretStr("super-secret-value"),
        llm_api_key=SecretStr("another-secret"),
    )
    text = repr(settings)
    assert "super-secret-value" not in text
    assert "another-secret" not in text


def test_docs_enabled_only_in_development():
    assert Settings(app_environment="development").docs_enabled is True

    production = Settings(
        app_environment="production",
        postgres_password=SecretStr("test-db-password"),
        llm_base_url="https://example.com/v1",
        llm_model="test-model",
        llm_api_key=SecretStr("test-llm-key"),
    )
    assert production.docs_enabled is False


def test_development_settings_allow_missing_credentials():
    settings = Settings(app_environment="development")

    assert settings.postgres_password.get_secret_value() == ""
    assert settings.llm_api_key.get_secret_value() == ""


def test_production_settings_reject_missing_credentials():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="Missing required production settings"):
        Settings(app_environment="production")


def test_production_settings_accept_all_required_credentials():
    settings = Settings(
        app_environment="production",
        postgres_password=SecretStr("test-db-password"),
        llm_base_url="https://example.com/v1",
        llm_model="test-model",
        llm_api_key=SecretStr("test-llm-key"),
    )

    assert settings.app_environment == "production"
