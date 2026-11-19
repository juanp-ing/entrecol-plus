"""Reportes en pantalla (JSON) y en PDF (RF-12 a RF-14, RF-16, RF-17).

Cada reporte tiene dos rutas: GET /api/reportes/{nombre} y GET /api/reportes/{nombre}/pdf
con los mismos parametros. Cada generacion queda registrada como evento REPORTE.
"""
import calendar
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from ..auditoria import registrar_evento
from ..reportes import consultas as q
from ..reportes.pdf import generar_pdf
from ..seguridad import Usuario, requiere_admin, usuario_actual

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

Orden = Query("asc", pattern="^(asc|desc)$", description="Orden de los nombres")


def _mes(txt: str, fin: bool) -> date:
    """MM/AAAA -> primer o ultimo dia del mes."""
    try:
        m, a = (int(x) for x in txt.split("/"))
        if not fin:
            return date(a, m, 1)
        return date(a, m, calendar.monthrange(a, m)[1])
    except (ValueError, AttributeError):
        raise HTTPException(422, f"Fecha invalida '{txt}', use MM/AAAA")


async def _responder(request: Request, u: Usuario, nombre: str, fn, pdf: bool):
    rep = await run_in_threadpool(fn)
    registrar_evento("REPORTE", u.usuario, f"{nombre} {'PDF' if pdf else 'pantalla'} {dict(request.query_params)}",
                     request.client.host if request.client else None)
    if not pdf:
        return rep
    contenido = await run_in_threadpool(generar_pdf, rep, u.usuario)
    return Response(contenido, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="entrecol-{nombre}.pdf"'})


@router.get("/nomina")
@router.get("/nomina/pdf", include_in_schema=False)
async def nomina(request: Request, orden: str = Orden, u: Usuario = Depends(usuario_actual)):
    return await _responder(request, u, "nomina", lambda: q.reporte_nomina(orden, u.usuario),
                            request.url.path.endswith("/pdf"))


@router.get("/personal")
@router.get("/personal/pdf", include_in_schema=False)
async def personal(request: Request, codigo: int = Query(...), u: Usuario = Depends(usuario_actual)):
    return await _responder(request, u, "personal", lambda: q.reporte_personal(codigo, u.usuario),
                            request.url.path.endswith("/pdf"))


@router.get("/salud-pension")
@router.get("/salud-pension/pdf", include_in_schema=False)
async def salud_pension(request: Request, orden: str = Orden, u: Usuario = Depends(usuario_actual)):
    return await _responder(request, u, "salud-pension", lambda: q.reporte_salud_pension(orden, u.usuario),
                            request.url.path.endswith("/pdf"))


@router.get("/novedades")
@router.get("/novedades/pdf", include_in_schema=False)
async def novedades(request: Request, desde: str = Query(..., description="MM/AAAA"),
                    hasta: str = Query(..., description="MM/AAAA"), orden: str = Orden,
                    u: Usuario = Depends(usuario_actual)):
    d, h = _mes(desde, False), _mes(hasta, True)
    if h < d:
        raise HTTPException(422, "La fecha final es anterior a la inicial")
    return await _responder(request, u, "novedades", lambda: q.reporte_novedades(d, h, orden, u.usuario),
                            request.url.path.endswith("/pdf"))


@router.get("/entretenimiento")
@router.get("/entretenimiento/pdf", include_in_schema=False)
async def entretenimiento(request: Request,
                          anio_desde: int = Query(1990, ge=1880, le=2100),
                          anio_hasta: int = Query(2000, ge=1880, le=2100),
                          n_top: int = Query(10, ge=1, le=500),
                          n_generos: int = Query(3, ge=0, le=20),
                          orden: str = Orden, u: Usuario = Depends(usuario_actual)):
    if anio_hasta < anio_desde:
        raise HTTPException(422, "El ano final es anterior al inicial")
    return await _responder(
        request, u, "entretenimiento",
        lambda: q.reporte_entretenimiento(anio_desde, anio_hasta, n_top, n_generos, orden, u.usuario),
        request.url.path.endswith("/pdf"))


@router.get("/auditoria")
@router.get("/auditoria/pdf", include_in_schema=False)
async def auditoria(request: Request, desde: date | None = None, hasta: date | None = None, usuario: str = "",
                    u: Usuario = Depends(requiere_admin)):
    hasta = hasta or date.today()
    desde = desde or hasta - timedelta(days=30)
    return await _responder(request, u, "auditoria", lambda: q.reporte_auditoria(desde, hasta, usuario, u.usuario),
                            request.url.path.endswith("/pdf"))
