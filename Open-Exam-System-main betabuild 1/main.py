import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response

from admin_routes import router as admin_router
from auth_routes import router as auth_router
from engine_helpers import read_config_data, serve_page_with_data
from site_routes import router as site_router
from student_routes import router as student_router
from teacher_exam_routes import router as teacher_exam_router
from system_admin_routes import router as system_admin_router
from account_store import ensure_default_teacher
from account_routes import router as account_router

app = FastAPI(title="Open Exam System")
logger = logging.getLogger("oes")
ensure_default_teacher()

if "OES_ADMIN_PASSWORD" not in os.environ or "OES_TEACHER_PASSWORD" not in os.environ:
    logger.warning("development_default_credentials_enabled change OES_ADMIN_PASSWORD and OES_TEACHER_PASSWORD before deployment")


@app.middleware("http")
async def request_logger(request: Request, call_next):
    if request.url.path.startswith("/sites/") or request.url.path.lower().endswith(".html"):
        logger.warning("direct_page_access_blocked path=%s", request.url.path)
        return Response(status_code=404)
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed method=%s path=%s", request.method, request.url.path)
        raise
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info("request method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, elapsed_ms)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/", response_class=HTMLResponse)
def get_login_page():
    return serve_page_with_data(folder_name="", file_name="index.html")


@app.get("/api/version")
def public_version():
    config = read_config_data()
    return {
        "version_number": config.get("version_number", "0.2.0-beta.1"),
        "release_date": config.get("release_date", ""),
        "release_channel": config.get("release_channel", "beta"),
    }


app.include_router(auth_router)
app.include_router(site_router)
app.include_router(admin_router)
app.include_router(teacher_exam_router)
app.include_router(student_router)
app.include_router(system_admin_router)
app.include_router(account_router)
