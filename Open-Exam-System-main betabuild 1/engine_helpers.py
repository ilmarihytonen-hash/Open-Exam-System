import json
import html
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SESSION_KEY_FILE = os.path.join(BASE_DIR, ".session.key")
SESSION_COOKIE = "oes_session"
DEFAULT_SESSION_TTL = timedelta(hours=8)
LOG_DIR = Path(BASE_DIR, "logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("oes")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    file_handler = logging.FileHandler(LOG_DIR / "oes.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def _get_fernet() -> Fernet:
    configured_key = os.getenv("OES_SESSION_KEY")
    if configured_key:
        return Fernet(configured_key.encode("ascii"))
    key_path = Path(SESSION_KEY_FILE)
    if not key_path.exists():
        key_path.write_bytes(Fernet.generate_key())
    return Fernet(key_path.read_bytes().strip())


def create_session(role: str, claims: dict | None = None) -> tuple[str, str]:
    csrf_token = secrets.token_urlsafe(32)
    try:
        session_hours = int(read_config_data().get("session_hours", 8))
    except (TypeError, ValueError):
        session_hours = 8
    session_ttl = timedelta(hours=max(1, min(session_hours, 168)))
    payload = {
        "role": role,
        "csrf": csrf_token,
        "expires": (datetime.now(timezone.utc) + session_ttl).isoformat(),
    }
    if claims:
        payload.update(claims)
    token = _get_fernet().encrypt(json.dumps(payload).encode("utf-8")).decode("ascii")
    logger.info("session_created role=%s", role)
    return token, csrf_token


def get_session(request: Request) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        logger.warning("session_missing path=%s", request.url.path)
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        session = json.loads(_get_fernet().decrypt(token.encode("ascii")).decode("utf-8"))
        expires = datetime.fromisoformat(session["expires"])
        if expires <= datetime.now(timezone.utc):
            raise ValueError("expired")
        return session
    except (InvalidToken, UnicodeDecodeError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        logger.warning("session_invalid path=%s", request.url.path)
        raise HTTPException(status_code=401, detail="Invalid or expired session")


def require_admin(request: Request) -> dict:
    return require_role(request, "admin")


def require_role(request: Request, role: str) -> dict:
    session = get_session(request)
    if session.get("role") != role:
        raise HTTPException(status_code=403, detail=f"{role.title()} access required")
    return session


def verify_csrf(request: Request, csrf_token: str, session: dict) -> None:
    if not secrets.compare_digest(csrf_token, session.get("csrf", "")):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

def serve_page_with_data(folder_name: str, file_name: str, dynamic_data: dict = None) -> HTMLResponse:
    """
    Reads an HTML file from any folder, injects updated data 
    into placeholder tags, and returns it to the browser.
    """
    # Build path dynamically whether it's in a subfolder or root
    if folder_name:
        root = Path(BASE_DIR, "sites", folder_name).resolve()
        file_path = (root / file_name).resolve()
        if root not in file_path.parents:
            raise HTTPException(status_code=404, detail="Page not found")
    else:
        file_path = Path(BASE_DIR, file_name).resolve()
        
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # If there is data to send to the website, swap out the placeholders
    if dynamic_data:
        for key, value in dynamic_data.items():
            placeholder = f"{{{{ {key} }}}}"
            html_content = html_content.replace(placeholder, html.escape(str(value)))
            
    return HTMLResponse(content=html_content)

def read_config_data() -> dict:
    """Reads current settings/info from config.json safely."""
    if not os.path.exists(CONFIG_FILE):
        logger.warning("config_missing path=%s", CONFIG_FILE)
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            logger.info("config_read keys=%s", sorted(data.keys()))
            return data
        except json.JSONDecodeError:
            logger.exception("config_invalid path=%s", CONFIG_FILE)
            return {}

def update_config_data(new_data: dict):
    """Updates config.json with newly submitted info from the website."""
    current_data = read_config_data()
    current_data.update(new_data)  # Merge old data with new data
    temporary_file = f"{CONFIG_FILE}.tmp"
    with open(temporary_file, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4)
        f.write("\n")
    os.replace(temporary_file, CONFIG_FILE)
    logger.info("config_updated keys=%s", sorted(new_data.keys()))
