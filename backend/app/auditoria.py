"""Registro de eventos sin cambio de datos (RF-16): logins, accesos, reportes y cargas.

Los cambios de datos los registran los triggers (db/03_triggers.sql).
"""
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .db import ejecutar

log = logging.getLogger("entrecol.auditoria")


def registrar_evento(tipo: str, usuario: str, detalle: str | None = None, ip: str | None = None) -> None:
    try:
        ejecutar(
            "INSERT INTO auditoria_evento (tipo, usuario_app, detalle, ip) VALUES (%s, %s, %s, %s)",
            (tipo, usuario, (detalle or "")[:500], ip),
            usuario=usuario,
        )
    except Exception:  # la auditoria nunca debe tumbar la peticion
        log.exception("No se pudo registrar el evento %s", tipo)


class AuditoriaMiddleware(BaseHTTPMiddleware):
    """Registra cada acceso autenticado a la API (metodo, ruta y codigo de respuesta).

    Los eventos LOGIN_*, REPORTE y CARGA_ARCHIVO los registran sus propias rutas con mas detalle.
    """

    async def dispatch(self, request: Request, call_next):
        respuesta = await call_next(request)
        usuario = getattr(request.state, "usuario", None)
        ruta = request.url.path
        if usuario and ruta.startswith("/api/") and not ruta.startswith(("/api/reportes", "/api/etl")):
            registrar_evento("ACCESO", usuario, f"{request.method} {ruta} -> {respuesta.status_code}",
                             request.client.host if request.client else None)
        return respuesta
