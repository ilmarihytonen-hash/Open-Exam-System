import hashlib
import hmac
import os
import secrets

from data_store import _connect, _now
from engine_helpers import logger


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = stored.split("$", 2)
        if algorithm != "scrypt":
            return False
        candidate = _hash_password(password, bytes.fromhex(salt_hex)).split("$", 2)[2]
        return hmac.compare_digest(candidate, digest_hex)
    except (ValueError, TypeError):
        return False


def initialize_accounts() -> None:
    with _connect() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS teacher_accounts (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, display_name TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL)"
        )
    logger.info("teacher_accounts_initialized")


def ensure_default_teacher() -> None:
    initialize_accounts()
    with _connect() as connection:
        exists = connection.execute("SELECT 1 FROM teacher_accounts WHERE username = 'teacher'").fetchone()
        if not exists:
            connection.execute(
                "INSERT INTO teacher_accounts(username, password_hash, display_name, created_at) VALUES (?, ?, ?, ?)",
                ("teacher", _hash_password(os.getenv("OES_TEACHER_PASSWORD", "teacher")), "Default Teacher", _now()),
            )
            logger.info("default_teacher_created")


def authenticate_teacher(username: str, password: str) -> dict | None:
    initialize_accounts()
    with _connect() as connection:
        row = connection.execute("SELECT * FROM teacher_accounts WHERE username = ? AND enabled = 1", (username,)).fetchone()
    if not row or not _verify_password(password, row["password_hash"]):
        return None
    return {"username": row["username"], "display_name": row["display_name"]}


def create_teacher_account(username: str, password: str, display_name: str) -> None:
    if not username or not password or len(password) < 10:
        raise ValueError("username and a password of at least 10 characters are required")
    initialize_accounts()
    with _connect() as connection:
        connection.execute(
            "INSERT INTO teacher_accounts(username, password_hash, display_name, created_at) VALUES (?, ?, ?, ?)",
            (username.strip().lower(), _hash_password(password), display_name.strip() or username.strip(), _now()),
        )
    logger.info("teacher_account_created username=%s", username.strip().lower())


def reset_teacher_password(username: str, password: str) -> bool:
    if not password or len(password) < 10:
        raise ValueError("password must be at least 10 characters")
    initialize_accounts()
    with _connect() as connection:
        result = connection.execute(
            "UPDATE teacher_accounts SET password_hash = ?, enabled = 1 WHERE username = ?",
            (_hash_password(password), username.strip().lower()),
        )
    logger.info("teacher_password_reset username=%s found=%s", username.strip().lower(), result.rowcount == 1)
    return result.rowcount == 1


def list_teacher_accounts() -> list[dict]:
    initialize_accounts()
    with _connect() as connection:
        rows = connection.execute("SELECT username, display_name, enabled, created_at FROM teacher_accounts ORDER BY username").fetchall()
    return [dict(row) for row in rows]


def set_teacher_enabled(username: str, enabled: bool) -> bool:
    initialize_accounts()
    with _connect() as connection:
        result = connection.execute("UPDATE teacher_accounts SET enabled = ? WHERE username = ?", (int(enabled), username))
    return result.rowcount == 1


ensure_default_teacher()
