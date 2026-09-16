from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from account_store import create_teacher_account, list_teacher_accounts, reset_teacher_password, set_teacher_enabled
from engine_helpers import require_admin, verify_csrf

router = APIRouter()


@router.get("/api/admin/teachers")
def teachers(request: Request):
    require_admin(request)
    return {"teachers": list_teacher_accounts()}


@router.post("/api/admin/teachers")
def add_teacher(request: Request, csrf_token: str = Form(...), username: str = Form(...), password: str = Form(...), display_name: str = Form("")):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    try:
        create_teacher_account(username, password, display_name)
    except ValueError as error:
        return HTMLResponse(str(error), status_code=400)
    return RedirectResponse("/admin/users", status_code=303)


@router.post("/api/admin/teachers/{username}/enabled")
def toggle_teacher(request: Request, username: str, csrf_token: str = Form(...), enabled: str = Form(...)):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    if not set_teacher_enabled(username, enabled.lower() == "true"):
        return HTMLResponse("Teacher account not found", status_code=404)
    return RedirectResponse("/admin/users", status_code=303)


@router.post("/api/admin/teachers/{username}/password")
def reset_teacher(request: Request, username: str, csrf_token: str = Form(...), password: str = Form(...)):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    try:
        found = reset_teacher_password(username, password)
    except ValueError as error:
        return HTMLResponse(str(error), status_code=400)
    if not found:
        return HTMLResponse("Teacher account not found", status_code=404)
    return RedirectResponse("/admin/users", status_code=303)
