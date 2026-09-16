import json
import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from data_store import create_exam, delete_exam, end_student_exam, get_exam, list_exams, monitor_exam, set_exam_status, stop_all_exams
from exam_schema import parse_questions_json
from engine_helpers import require_role, verify_csrf

router = APIRouter()
logger = logging.getLogger("oes")


def _teacher_name(request: Request) -> str:
    return require_role(request, "teacher").get("teacher_username", "teacher")


@router.get("/api/teacher/exams")
def teacher_exams(request: Request):
    return {"exams": list_exams(_teacher_name(request))}


@router.post("/api/teacher/exams")
def create_teacher_exam(
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    questions: str = Form("[]"),
    parts: str = Form("Part 1"),
    lock_parts: str = Form("true"),
):
    session = require_role(request, "teacher")
    verify_csrf(request, csrf_token, session)
    try:
        parsed_questions = parse_questions_json(questions)
    except ValueError as error:
        return HTMLResponse(f"Invalid questions: {error}", status_code=400)
    part_names = [part.strip() for part in parts.split(",") if part.strip()]
    if not part_names:
        return HTMLResponse("At least one exam part is required", status_code=400)
    exam_id = create_exam(
        session.get("teacher_username", "teacher"),
        title.strip(),
        description.strip(),
        parsed_questions,
        {"parts": part_names, "lock_parts": lock_parts.lower() == "true"},
    )
    return RedirectResponse(f"/teacher/exam-maker?created={exam_id}", status_code=303)


@router.post("/api/teacher/exams/{exam_id}/status")
def change_exam_status(request: Request, exam_id: str, csrf_token: str = Form(...), status: str = Form(...)):
    session = require_role(request, "teacher")
    verify_csrf(request, csrf_token, session)
    changed = set_exam_status(exam_id, session.get("teacher_username", "teacher"), status)
    if not changed:
        return HTMLResponse("Exam not found or not owned by this teacher", status_code=404)
    return RedirectResponse("/teacher/exam-status", status_code=303)


@router.post("/api/teacher/exams/stop-all")
def stop_all_teacher_exams(request: Request, csrf_token: str = Form(...)):
    session = require_role(request, "teacher")
    verify_csrf(request, csrf_token, session)
    stop_all_exams(session.get("teacher_username", "teacher"))
    return RedirectResponse("/teacher/exam-status", status_code=303)


@router.get("/api/teacher/exams/{exam_id}/monitor")
def monitor_teacher_exam(request: Request, exam_id: str):
    teacher = _teacher_name(request)
    exam = get_exam(exam_id)
    if not exam or exam["teacher_username"] != teacher:
        return HTMLResponse("Exam not found", status_code=404)
    return {"exam": exam, **monitor_exam(exam_id)}


@router.post("/api/teacher/exams/{exam_id}/delete")
def delete_teacher_exam(request: Request, exam_id: str, csrf_token: str = Form(...)):
    session = require_role(request, "teacher")
    verify_csrf(request, csrf_token, session)
    if not delete_exam(exam_id, session.get("teacher_username", "teacher")):
        return HTMLResponse("Exam not found or not owned by this teacher", status_code=404)
    return RedirectResponse("/teacher/exam-maker", status_code=303)


@router.post("/api/teacher/exams/{exam_id}/students/{student_id}/end")
def end_student(request: Request, exam_id: str, student_id: str, csrf_token: str = Form(...)):
    session = require_role(request, "teacher")
    verify_csrf(request, csrf_token, session)
    exam = get_exam(exam_id)
    if not exam or exam["teacher_username"] != session.get("teacher_username", "teacher"):
        return HTMLResponse("Exam not found", status_code=404)
    if not end_student_exam(exam_id, student_id):
        return HTMLResponse("Student session not found", status_code=404)
    return RedirectResponse("/teacher/exam-status", status_code=303)
