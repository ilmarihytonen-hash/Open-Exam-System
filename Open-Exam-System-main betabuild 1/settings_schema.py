from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Setting:
    key: str
    category: str
    default: Any
    description: str
    validator: Callable[[str], Any]
    kind: str = "text"


def text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("value cannot be empty")
    return value


def optional_text(value: str) -> str:
    return value.strip()


def boolean(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false", "1", "0", "yes", "no"}:
        raise ValueError("expected true or false")
    return normalized in {"true", "1", "yes"}


def integer(value: str) -> int:
    return int(value.strip())


def bounded_integer(minimum: int, maximum: int) -> Callable[[str], int]:
    def validate(value: str) -> int:
        result = integer(value)
        if not minimum <= result <= maximum:
            raise ValueError(f"must be between {minimum} and {maximum}")
        return result
    return validate


def csv_text(value: str) -> str:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        raise ValueError("at least one item is required")
    return ",".join(parts)


SETTINGS = [
    Setting("application_name", "system", "text", "Open Exam System", "Displayed application name", text),
    Setting("status", "system", "text", "Operational", "Displayed system status", text),
    Setting("server_host", "network", "127.0.0.1", "Server bind host", text),
    Setting("server_port", "network", "8000", "Server bind port", bounded_integer(1, 65535)),
    Setting("network_public_url", "network", "", "Public HTTPS URL", optional_text),
    Setting("network_allowed_cidrs", "network", "127.0.0.1/32", "Allowed management CIDRs", csv_text),
    Setting("firewall_backend", "network", "ufw", "Firewall command backend", text),
    Setting("firewall_enabled", "network", "false", "Whether the firewall is managed", boolean),
    Setting("https_only", "security", "false", "Require HTTPS deployment", boolean),
    Setting("session_hours", "security", "8", "Session lifetime in hours", bounded_integer(1, 168)),
    Setting("session_cookie_secure", "security", "false", "Set Secure on session cookies", boolean),
    Setting("log_level", "security", "INFO", "Application log level", text),
    Setting("log_retention_days", "security", "30", "Log retention period", bounded_integer(1, 3650)),
    Setting("database_url", "database", "sqlite:///data/oes.sqlite3", "Exam database URL", text),
    Setting("database_wal", "database", "true", "Enable SQLite write-ahead logging", boolean),
    Setting("database_backup_enabled", "database", "false", "Enable scheduled database backups", boolean),
    Setting("database_backup_dir", "database", "data/backups", "Database backup directory", text),
    Setting("database_backup_interval", "database", "3600", "Backup interval in seconds", bounded_integer(60, 604800)),
    Setting("database_max_size_mb", "database", "2048", "Database size warning threshold", bounded_integer(10, 1048576)),
    Setting("ssh_host", "ssh", "", "SSH management host", optional_text),
    Setting("ssh_port", "ssh", "22", "SSH management port", bounded_integer(1, 65535)),
    Setting("ssh_user", "ssh", "oesadmin", "SSH management user", text),
    Setting("ssh_key_path", "ssh", "", "SSH private key path; never a password", optional_text),
    Setting("ssh_known_hosts", "ssh", "~/.ssh/known_hosts", "SSH known-hosts file", text),
    Setting("ssh_connect_timeout", "ssh", "5", "SSH connection timeout seconds", bounded_integer(1, 120)),
    Setting("ssh_allow_poweroff", "ssh", "false", "Allow configured SSH poweroff action", boolean),
    Setting("cluster_enabled", "cluster", "false", "Enable cluster routing", boolean),
    Setting("cluster_discovery_cidr", "cluster", "", "Private CIDR used for discovery", optional_text),
    Setting("cluster_discovery_port", "cluster", "8000", "Cluster service port", bounded_integer(1, 65535)),
    Setting("cluster_replication_mode", "cluster", "primary-replica", "Replication mode", text),
    Setting("student_require_name", "students", "true", "Require student name", boolean),
    Setting("student_require_dob", "students", "true", "Require student date of birth", boolean),
    Setting("student_require_email", "students", "true", "Require and validate student email", boolean),
    Setting("student_allowed_apps", "students", "firefox,plasmashell,kwin_wayland", "Allowed client applications", csv_text),
    Setting("student_forbidden_apps", "students", "chromium,google-chrome,libreoffice,code,konsole", "Forbidden client applications", csv_text),
    Setting("student_exam_url", "students", "http://127.0.0.1:8000/student/login", "Student exam URL", text),
    Setting("student_sync_interval", "students", "1", "Answer sync interval seconds", bounded_integer(1, 60)),
]

SETTING_MAP = {setting.key: setting for setting in SETTINGS}


def schema() -> list[dict[str, Any]]:
    return [
        {"key": setting.key, "category": setting.category, "kind": setting.kind, "default": setting.default, "description": setting.description}
        for setting in SETTINGS
    ]


def normalize(key: str, value: str) -> Any:
    setting = SETTING_MAP.get(key)
    if setting is None:
        raise KeyError(key)
    return setting.validator(value)
