from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from engine_helpers import read_config_data, require_admin, require_role, serve_page_with_data

router = APIRouter()

ADMIN_PAGES = {
    "dashboard": "admistrator-dashboard.html",
    "network": "networksettings.html",
    "security": "security-settings.html",
    "cluster": "cluster-settings.html",
    "database": "database-settings.html",
    "ssh": "ssh-settings.html",
    "system": "system-settings.html",
    "students": "student-settings.html",
    "users": "user-settings.html",
    "server-status": "server-status.html",
    "exam-status": "exam-status.html",
    "logs": "logs.html",
    "version": "admistrator-version-info.html",
    "license": "admistrator-License & Info.html",
}

TEACHER_PAGES = {
    "dashboard": "teacher-dashboard.html",
    "exam-status": "teacher-exam-status.html",
    "students": "teacher-students.html",
    "exam-maker": "teacher-exam-maker.html",
    "preview-exam": "teacher-preview-exam.html",
    "logs": "teacher-logs.html",
    "version": "teacher-version-info.html",
    "license": "teacher-License & Info.html",
}


def _page_data(request: Request, role_label: str) -> dict:
    session = require_admin(request) if role_label == "Administrator" else require_role(request, "teacher")
    settings = read_config_data()
    return {
        "csrf_token": session["csrf"],
        "system_version": settings.get("version_number", "1.0.0"),
        "user_role": role_label,
    }


@router.get("/admin/{page}", response_class=HTMLResponse)
def admin_page(page: str, request: Request):
    file_name = ADMIN_PAGES.get(page)
    if not file_name:
        return HTMLResponse("Page not found", status_code=404)
    return serve_page_with_data("admistrator-sites", file_name, _page_data(request, "Administrator"))


@router.get("/teacher/{page}", response_class=HTMLResponse)
def teacher_page(page: str, request: Request):
    file_name = TEACHER_PAGES.get(page)
    if not file_name:
        return HTMLResponse("Page not found", status_code=404)
    return serve_page_with_data("teacher-sites", file_name, _page_data(request, "Teacher"))
