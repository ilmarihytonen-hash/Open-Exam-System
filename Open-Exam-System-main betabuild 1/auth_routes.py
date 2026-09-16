import logging
import os

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from account_store import authenticate_teacher
from engine_helpers import SESSION_COOKIE, create_session, read_config_data

router = APIRouter()
logger = logging.getLogger("oes")


@router.post("/login")
def handle_login(username: str = Form(...), password: str = Form(...)):
    role = username.strip().lower()
    admin_username = os.getenv("OES_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("OES_ADMIN_PASSWORD", "admin")
    secure_cookie = os.getenv("OES_COOKIE_SECURE") == "1" or bool(read_config_data().get("session_cookie_secure", False))

    if role == admin_username.lower() and password == admin_password:
        token, _ = create_session("admin")
        response = RedirectResponse("/admin/dashboard", status_code=303)
        response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=secure_cookie, max_age=28800)
        return response

    teacher = authenticate_teacher(role, password)
    if teacher:
        token, _ = create_session("teacher", {"teacher_username": teacher["username"], "teacher_display_name": teacher["display_name"]})
        response = RedirectResponse("/teacher/dashboard", status_code=303)
        response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=secure_cookie, max_age=28800)
        return response

    logger.warning("login_failed username=%s", role)
    return HTMLResponse("<h2>Invalid Login Credentials</h2>", status_code=401)


@router.post("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response
