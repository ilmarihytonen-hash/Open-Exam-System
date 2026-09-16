import re
from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from data_store import get_exam, list_exams, record_violation, save_answers, upsert_student
from engine_helpers import SESSION_COOKIE, create_session, read_config_data, require_role, serve_page_with_data

router = APIRouter()
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _required(config: dict, key: str, default: bool = True) -> bool:
    value = config.get(key, default)
    return value is True or str(value).lower() == "true"


@router.get("/student/login", response_class=HTMLResponse)
def student_login_page():
    return serve_page_with_data("student-sites", "student-login.html")


@router.post("/student/login")
def student_login(
    name: str = Form(""),
    date_of_birth: str = Form(""),
    email: str = Form(""),
):
    config = read_config_data()
    name = name.strip()
    date_of_birth = date_of_birth.strip()
    email = email.strip().lower()
    if _required(config, "student_require_name") and not name:
        return HTMLResponse("Name is required", status_code=400)
    if _required(config, "student_require_dob"):
        try:
            date.fromisoformat(date_of_birth)
        except ValueError:
            return HTMLResponse("A valid date of birth is required", status_code=400)
    if _required(config, "student_require_email") and not EMAIL_PATTERN.fullmatch(email):
        return HTMLResponse("A valid email address is required", status_code=400)
    student_id = upsert_student(name, date_of_birth or None, email or None)
    token, _ = create_session("student", {"student_id": student_id, "student_name": name, "student_email": email})
    response = RedirectResponse("/student/exams", status_code=303)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=28800)
    return response


@router.get("/student/exams", response_class=HTMLResponse)
def student_exams(request: Request):
    require_role(request, "student")
    exams = list_exams(active_only=True)
    links = "".join(f'<li><a href="/student/exam/{exam["id"]}">{exam["title"]}</a></li>' for exam in exams)
    body = f"<!doctype html><html><head><meta charset=\"utf-8\"><title>Available exams</title></head><body><h1>Available exams</h1><ul>{links or '<li>No active exams</li>'}</ul></body></html>"
    return HTMLResponse(body)


@router.get("/student/exam/{exam_id}", response_class=HTMLResponse)
def student_exam_page(request: Request, exam_id: str):
    require_role(request, "student")
    exam = get_exam(exam_id)
    if not exam or exam["status"] != "active":
        return HTMLResponse("Exam is not active", status_code=404)
    return serve_page_with_data("student-sites", "student-exam.html", {"exam_id": exam_id, "exam_title": exam["title"]})


@router.get("/api/student/exams/{exam_id}")
def student_exam_data(request: Request, exam_id: str):
    require_role(request, "student")
    exam = get_exam(exam_id)
    if not exam or exam["status"] != "active":
        return HTMLResponse("Exam is not active", status_code=404)
    return {"exam": exam}


@router.post("/api/student/exams/{exam_id}/answers")
def sync_student_answers(request: Request, exam_id: str, payload: dict):
    session = require_role(request, "student")
    exam = get_exam(exam_id)
    if not exam or exam["status"] != "active":
        return HTMLResponse("Exam is not active", status_code=404)
    answers = payload.get("answers", payload)
    if not isinstance(answers, dict):
        return HTMLResponse("Answers must be an object", status_code=400)
    try:
        save_answers(exam_id, session["student_id"], answers)
    except ValueError as error:
        return HTMLResponse(str(error), status_code=403)
    return {"saved": True}


@router.post("/api/student/exams/{exam_id}/violations")
def report_student_violation(request: Request, exam_id: str, payload: dict):
    session = require_role(request, "student")
    exam = get_exam(exam_id)
    if not exam or exam["status"] != "active":
        return HTMLResponse("Exam is not active", status_code=404)
    record_violation(exam_id, session["student_id"], str(payload.get("kind", "unknown")), str(payload.get("details", "")))
    return {"recorded": True}
