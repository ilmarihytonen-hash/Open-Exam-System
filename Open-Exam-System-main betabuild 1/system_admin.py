import json
import logging
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("oes")
SERVICE_PATTERN = re.compile(r"^[A-Za-z0-9_.@-]+\.service$")


def _debian_only() -> None:
    if platform.system() != "Linux":
        raise RuntimeError("Debian system controls are available only on Linux")


def _run(command: list[str], timeout: int = 10) -> str:
    _debian_only()
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"command failed: {result.returncode}")
    return result.stdout.strip()


def _sudo_enabled() -> bool:
    return os.getenv("OES_ALLOW_SYSTEM_CHANGES") == "1"


def _sudo(command: list[str]) -> str:
    if not _sudo_enabled():
        raise RuntimeError("System changes are disabled; set OES_ALLOW_SYSTEM_CHANGES=1 after configuring sudoers")
    return _run(["sudo", "-n", *command], timeout=30)


def _managed_service(service: str) -> str:
    if not SERVICE_PATTERN.fullmatch(service):
        raise ValueError("Invalid service name")
    allowed = {item.strip() for item in os.getenv("OES_MANAGED_SERVICES", "oes-server.service").split(",") if item.strip()}
    if service not in allowed:
        raise ValueError("Service is not in OES_MANAGED_SERVICES")
    return service


def overview() -> dict[str, Any]:
    if platform.system() != "Linux":
        return {"supported": False, "platform": platform.platform()}
    disk = shutil.disk_usage("/")
    result: dict[str, Any] = {
        "supported": True,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "disk": {"total": disk.total, "used": disk.used, "free": disk.free},
    }
    try:
        result["hostnamectl"] = _run(["hostnamectl", "status"])
    except (RuntimeError, FileNotFoundError) as error:
        result["hostnamectl_error"] = str(error)
    for name, command in {
        "addresses": ["ip", "-j", "addr"],
        "routes": ["ip", "-j", "route"],
        "listening": ["ss", "-lntup"],
        "firewall": ["ufw", "status"],
        "upgradable": ["apt", "list", "--upgradable"],
    }.items():
        try:
            value = _run(command, timeout=15)
            result[name] = json.loads(value) if name in {"addresses", "routes"} else value[-12000:]
        except (RuntimeError, FileNotFoundError, json.JSONDecodeError) as error:
            result[f"{name}_error"] = str(error)
    return result


def service_action(service: str, action: str) -> str:
    service = _managed_service(service)
    if action not in {"start", "stop", "restart", "enable", "disable"}:
        raise ValueError("Unsupported service action")
    return _sudo(["systemctl", action, service])


def set_hostname(hostname: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,62}", hostname):
        raise ValueError("Invalid hostname")
    return _sudo(["hostnamectl", "set-hostname", hostname])


def set_timezone(timezone: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._+-]+/[A-Za-z0-9._+-]+", timezone):
        raise ValueError("Invalid timezone")
    return _sudo(["timedatectl", "set-timezone", timezone])


def power_action(action: str, confirmation: str) -> str:
    if action not in {"reboot", "poweroff"} or confirmation != action:
        raise ValueError("Action and confirmation must match")
    return _sudo(["systemctl", action])
