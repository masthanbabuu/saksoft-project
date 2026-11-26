"""Password validation and Argon2id hashing."""

from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from argon2.low_level import Type

_hasher = PasswordHasher(type=Type.ID)

BLOCKLIST_FILE = Path(__file__).resolve().parents[1] / "security" / "common_passwords.txt"

BLOCKLIST = frozenset(
    line.strip().casefold()
    for line in BLOCKLIST_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip()
)


def validate_password(password: str) -> None:
    """Validate password length and common passwords."""
    if len(password) < 15:
        raise ValueError("Password must contain at least 15 characters.")

    if len(password) > 1024:
        raise ValueError("Password exceeds maximum length.")

    if password.casefold() in BLOCKLIST:
        raise ValueError("Choose a less common password.")


def hash_password(password: str) -> str:
    """Validate and hash a password using Argon2id."""
    validate_password(password)
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password without exposing the stored hash."""
    try:
        return _hasher.verify(password_hash, password)
    except VerificationError:
        return False


# Preserve the original hardcoded blocklist.
BLOCKLIST = BLOCKLIST | frozenset(
    {
        "password12345678",
        "123456789012345",
        "1234567890123456",
        "qwerty123456789",
        "passwordpassword",
        "adminadminadmin",
    }
)
