import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from cluster_manager import cluster_manager
from data_store import delete_all_exam_data
from engine_helpers import read_config_data, require_admin, update_config_data, verify_csrf
from settings_schema import normalize, schema

router = APIRouter()
logger = logging.getLogger("oes")

@router.get("/api/admin/config")
def get_admin_config(request: Request):
    require_admin(request)
    return {"config": read_config_data(), "schema": schema()}


@router.post("/api/admin/config")
def update_admin_config(request: Request, csrf_token: str = Form(...), key: str = Form(...), value: str = Form(...)):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    try:
        normalized_value = normalize(key, value)
    except (KeyError, ValueError) as error:
        logger.warning("config_update_rejected key=%s", key)
        return HTMLResponse(f"Invalid setting: {error}", status_code=400)
    update_config_data({key: normalized_value})
    return RedirectResponse("/admin/dashboard", status_code=303)


@router.get("/api/admin/cluster")
def get_cluster_status(request: Request):
    require_admin(request)
    return cluster_manager.status()


@router.post("/api/admin/cluster/settings")
def update_cluster_settings(
    request: Request,
    csrf_token: str = Form(...),
    enabled: str = Form(...),
    discovery_cidr: str = Form(""),
    discovery_port: int = Form(8000),
    replication_mode: str = Form("primary-replica"),
):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    if discovery_port < 1 or discovery_port > 65535:
        return HTMLResponse("Invalid cluster port", status_code=400)
    if replication_mode not in {"primary-replica", "active-active"}:
        return HTMLResponse("Invalid replication mode", status_code=400)
    update_config_data({
        "cluster_enabled": enabled.lower() == "true",
        "cluster_discovery_cidr": discovery_cidr.strip(),
        "cluster_discovery_port": discovery_port,
        "cluster_replication_mode": replication_mode,
    })
    return RedirectResponse("/admin/cluster", status_code=303)


@router.post("/api/admin/cluster/discover")
def discover_cluster(
    request: Request,
    csrf_token: str = Form(...),
    cidr: str = Form(...),
    port: int = Form(8000),
):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    try:
        cluster_manager.discover(cidr.strip(), port)
    except (ValueError, OSError) as error:
        logger.warning("cluster_discovery_rejected cidr=%s port=%s error=%s", cidr, port, error)
        return HTMLResponse(f"Discovery failed: {error}", status_code=400)
    return RedirectResponse("/admin/cluster", status_code=303)


@router.post("/api/admin/cluster/check")
def check_cluster(request: Request, csrf_token: str = Form(...)):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    cluster_manager.check_all()
    return RedirectResponse("/admin/cluster", status_code=303)


@router.post("/api/admin/exam-data/delete-all")
def delete_all_exam_data_route(request: Request, csrf_token: str = Form(...)):
    session = require_admin(request)
    verify_csrf(request, csrf_token, session)
    delete_all_exam_data()
    return RedirectResponse("/admin/dashboard", status_code=303)
