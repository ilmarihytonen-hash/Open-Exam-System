import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine_helpers import BASE_DIR, logger, read_config_data

DATA_DIR = Path(BASE_DIR, "data")
DEFAULT_DATABASE_PATH = DATA_DIR / "oes.sqlite3"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    database_url = str(read_config_data().get("database_url", "sqlite:///data/oes.sqlite3"))
    if not database_url.startswith("sqlite:///"):
        raise RuntimeError("Only sqlite:/// database URLs are supported by the local exam store")
    configured_path = Path(database_url.removeprefix("sqlite:///"))
    database_path = configured_path if configured_path.is_absolute() else Path(BASE_DIR, configured_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    wal_enabled = read_config_data().get("database_wal", True)
    connection.execute(f"PRAGMA journal_mode={'WAL' if str(wal_enabled).lower() == 'true' else 'DELETE'}")
    return connection


def initialize_database() -> None:
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date_of_birth TEXT,
                email TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS exams (
                id TEXT PRIMARY KEY,
                teacher_username TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                questions_json TEXT NOT NULL DEFAULT '[]',
                settings_json TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                started_at TEXT,
                ended_at TEXT
            );
            CREATE TABLE IF NOT EXISTS exam_answers (
                exam_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                answers_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (exam_id, student_id),
                FOREIGN KEY (exam_id) REFERENCES exams(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            );
            CREATE TABLE IF NOT EXISTS exam_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (exam_id) REFERENCES exams(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            );
            CREATE TABLE IF NOT EXISTS exam_participants (
                exam_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                last_seen TEXT NOT NULL,
                PRIMARY KEY (exam_id, student_id)
            );
            CREATE INDEX IF NOT EXISTS idx_answers_exam ON exam_answers(exam_id);
            CREATE INDEX IF NOT EXISTS idx_violations_exam ON exam_violations(exam_id);
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(exams)").fetchall()}
        if "settings_json" not in columns:
            connection.execute("ALTER TABLE exams ADD COLUMN settings_json TEXT NOT NULL DEFAULT '{}'")
    logger.info("database_initialized path=%s", DEFAULT_DATABASE_PATH)


def upsert_student(name: str, date_of_birth: str | None, email: str | None) -> str:
    student_id = str(uuid.uuid4())
    with _connect() as connection:
        connection.execute(
            "INSERT INTO students(id, name, date_of_birth, email, created_at) VALUES (?, ?, ?, ?, ?)",
            (student_id, name, date_of_birth, email, _now()),
        )
    return student_id


def create_exam(teacher_username: str, title: str, description: str, questions: list[Any], settings: dict[str, Any] | None = None) -> str:
    exam_id = str(uuid.uuid4())
    with _connect() as connection:
        connection.execute(
            "INSERT INTO exams(id, teacher_username, title, description, questions_json, settings_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (exam_id, teacher_username, title, description, json.dumps(questions), json.dumps(settings or {"lock_parts": True}), _now()),
        )
    logger.info("exam_created exam_id=%s teacher=%s", exam_id, teacher_username)
    return exam_id


def list_exams(teacher_username: str | None = None, active_only: bool = False) -> list[dict[str, Any]]:
    query = "SELECT * FROM exams"
    values: list[Any] = []
    clauses = []
    if teacher_username is not None:
        clauses.append("teacher_username = ?")
        values.append(teacher_username)
    if active_only:
        clauses.append("status = 'active'")
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY created_at DESC"
    with _connect() as connection:
        rows = connection.execute(query, values).fetchall()
    return [_exam_row(row) for row in rows]


def get_exam(exam_id: str) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    return _exam_row(row) if row else None


def _exam_row(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["questions"] = json.loads(result.pop("questions_json"))
    result["settings"] = json.loads(result.pop("settings_json", "{}"))
    return result


def set_exam_status(exam_id: str, teacher_username: str, status: str) -> bool:
    if status not in {"draft", "active", "stopped"}:
        raise ValueError("invalid exam status")
    timestamp = _now() if status == "active" else None
    with _connect() as connection:
        result = connection.execute(
            "UPDATE exams SET status = ?, started_at = COALESCE(started_at, ?), ended_at = ? WHERE id = ? AND teacher_username = ?",
            (status, timestamp, _now() if status == "stopped" else None, exam_id, teacher_username),
        )
    return result.rowcount == 1


def delete_exam(exam_id: str, teacher_username: str) -> bool:
    with _connect() as connection:
        connection.execute("DELETE FROM exam_participants WHERE exam_id = ?", (exam_id,))
        result = connection.execute("DELETE FROM exams WHERE id = ? AND teacher_username = ?", (exam_id, teacher_username))
    logger.info("exam_deleted exam_id=%s teacher=%s deleted=%s", exam_id, teacher_username, result.rowcount == 1)
    return result.rowcount == 1


def delete_all_exam_data() -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM exam_violations")
        connection.execute("DELETE FROM exam_participants")
        connection.execute("DELETE FROM exam_answers")
        connection.execute("DELETE FROM exams")
        connection.execute("DELETE FROM students")
    logger.warning("all_exam_data_deleted")


def save_answers(exam_id: str, student_id: str, answers: dict[str, Any]) -> None:
    with _connect() as connection:
        participant = connection.execute("SELECT status FROM exam_participants WHERE exam_id = ? AND student_id = ?", (exam_id, student_id)).fetchone()
        if participant and participant["status"] == "ended":
            raise ValueError("student exam session has ended")
        connection.execute(
            "INSERT INTO exam_participants(exam_id, student_id, status, last_seen) VALUES (?, ?, 'active', ?) ON CONFLICT(exam_id, student_id) DO UPDATE SET last_seen=excluded.last_seen",
            (exam_id, student_id, _now()),
        )
        connection.execute(
            "INSERT INTO exam_answers(exam_id, student_id, answers_json, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(exam_id, student_id) DO UPDATE SET answers_json=excluded.answers_json, updated_at=excluded.updated_at",
            (exam_id, student_id, json.dumps(answers), _now()),
        )


def end_student_exam(exam_id: str, student_id: str) -> bool:
    with _connect() as connection:
        result = connection.execute("UPDATE exam_participants SET status = 'ended' WHERE exam_id = ? AND student_id = ?", (exam_id, student_id))
    return result.rowcount == 1


def stop_all_exams(teacher_username: str) -> int:
    with _connect() as connection:
        result = connection.execute("UPDATE exams SET status = 'stopped', ended_at = ? WHERE teacher_username = ? AND status = 'active'", (_now(), teacher_username))
    return result.rowcount


def record_violation(exam_id: str, student_id: str, kind: str, details: str) -> None:
    with _connect() as connection:
        connection.execute(
            "INSERT INTO exam_violations(exam_id, student_id, kind, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (exam_id, student_id, kind, details, _now()),
        )
    logger.warning("student_violation exam_id=%s student_id=%s kind=%s", exam_id, student_id, kind)


def monitor_exam(exam_id: str) -> dict[str, Any]:
    with _connect() as connection:
        students = connection.execute(
            "SELECT p.student_id, p.status, p.last_seen, s.name, s.date_of_birth, s.email "
            "FROM exam_participants p JOIN students s ON s.id = p.student_id "
            "WHERE p.exam_id = ? ORDER BY p.last_seen DESC",
            (exam_id,),
        ).fetchall()
        answers = connection.execute(
            "SELECT student_id, answers_json, updated_at FROM exam_answers WHERE exam_id = ?",
            (exam_id,),
        ).fetchall()
        violations = connection.execute(
            "SELECT student_id, kind, details, created_at FROM exam_violations "
            "WHERE exam_id = ? ORDER BY created_at DESC",
            (exam_id,),
        ).fetchall()
    return {
        "students": [dict(row) for row in students],
        "answers": [{**dict(row), "answers": json.loads(row["answers_json"])} for row in answers],
        "violations": [dict(row) for row in violations],
    }


initialize_database()
