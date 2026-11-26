from pathlib import Path

PASSWORD_FILE = Path(__file__).parent / "common_passwords.txt"


def is_common_password(password: str) -> bool:
    common_passwords = {line.strip() for line in PASSWORD_FILE.read_text().splitlines()}
    return password.lower() in common_passwords
