"""Salud del servicio (Sprint 28): para el balanceador y el contenedor. Sin datos ni autenticación."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health(request: Request) -> JSONResponse:
    """200 si la API responde y la base de datos contesta; 503 si la base no está disponible."""
    try:
        with request.app.state.session_factory() as session:
            session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 — cualquier falla de la base se reporta igual, sin detalles
        return JSONResponse({"status": "db_unavailable"}, status_code=503)
    return JSONResponse({"status": "ok"})
