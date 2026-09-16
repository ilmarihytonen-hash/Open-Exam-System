import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from engine_helpers import require_admin, verify_csrf
from system_admin import overview, power_action, service_action, set_hostname, set_timezone

router = APIRouter()
logger = logging.getLogger("oes")


def _change_session(request: Request, csrf_token: str) -> dict:
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    return session


@router.get("/api/admin/server/overview")
def server_overview(request: Request):
    require_admin(request)
    return overview()


@router.post("/api/admin/server/service")
def server_service(request: Request, csrf_token: str = Form(...), service: str = Form(...), action: str = Form(...)):
    _change_session(request, csrf_token)
    try:
        output = service_action(service, action)
    except (RuntimeError, ValueError, OSError) as error:
        logger.warning("server_service_failed service=%s action=%s error=%s", service, action, error)
        return HTMLResponse(str(error), status_code=400)
    return {"ok": True, "output": output}


@router.post("/api/admin/server/hostname")
def server_hostname(request: Request, csrf_token: str = Form(...), hostname: str = Form(...)):
    _change_session(request, csrf_token)
    try:
        output = set_hostname(hostname.strip())
    except (RuntimeError, ValueError, OSError) as error:
        logger.warning("server_hostname_failed error=%s", error)
        return HTMLResponse(str(error), status_code=400)
    return {"ok": True, "output": output}


@router.post("/api/admin/server/timezone")
def server_timezone(request: Request, csrf_token: str = Form(...), timezone: str = Form(...)):
    _change_session(request, csrf_token)
    try:
        output = set_timezone(timezone.strip())
    except (RuntimeError, ValueError, OSError) as error:
        logger.warning("server_timezone_failed error=%s", error)
        return HTMLResponse(str(error), status_code=400)
    return {"ok": True, "output": output}


@router.post("/api/admin/server/power")
def server_power(request: Request, csrf_token: str = Form(...), action: str = Form(...), confirmation: str = Form(...)):
    _change_session(request, csrf_token)
    try:
        output = power_action(action, confirmation)
    except (RuntimeError, ValueError, OSError) as error:
        logger.warning("server_power_failed action=%s error=%s", action, error)
        return HTMLResponse(str(error), status_code=400)
    return {"ok": True, "output": output}
