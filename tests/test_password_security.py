import pytest

from app.services.password_security import (
    BLOCKLIST,
    hash_password,
    validate_password,
    verify_password,
)


def test_common_password_rejected():
    with pytest.raises(ValueError, match="less common"):
        validate_password("password12345678")


def test_dictionary_password_rejected():
    assert "password" in BLOCKLIST


def test_short_password_rejected():
    with pytest.raises(ValueError, match="15 characters"):
        validate_password("short")


def test_strong_password_accepted():
    validate_password("MySecurePass@2026")


def test_password_hashing_and_verification():
    test_secret = "MySecurePass@2026"  # noqa: S105
    hashed = hash_password(test_secret)

    assert hashed != test_secret
    assert verify_password(test_secret, hashed)
    assert not verify_password("WrongPassword@2026", hashed)
