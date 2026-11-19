"""Carga y recarga de archivos (RF-05 a RF-10). Solo ADMINISTRADOR.

Flujo: leer -> validar estructura y tipos -> limpiar -> insertar en UNA transaccion -> resumen.
Si la estructura falla, nada se escribe; si la insercion falla, se hace rollback completo.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from ..auditoria import registrar_evento
from ..db import conexion
from ..etl import libros, nomina, peliculas
from ..etl.comun import ErrorEstructura
from ..seguridad import Usuario, requiere_admin

router = APIRouter(prefix="/api/etl", tags=["ETL"])

MAX_BYTES = 50 * 1024 * 1024


async def _leer(archivo: UploadFile, extensiones: tuple[str, ...]) -> bytes:
    if not (archivo.filename or "").lower().endswith(extensiones):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Extension no permitida, se espera {' o '.join(extensiones)}")
    contenido = await archivo.read()
    if len(contenido) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "El archivo supera 50 MB")
    return contenido


def _ejecutar(request: Request, u: Usuario, nombre: str, parsear, cargar):
    try:
        datos, resumen = parsear()
    except ErrorEstructura as exc:
        registrar_evento("CARGA_ARCHIVO", u.usuario, f"{nombre}: RECHAZADO - {exc}", request.client.host if request.client else None)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Estructura invalida: {exc}")
    with conexion(u.usuario) as con, con.cursor() as cur:
        cargar(cur, datos, resumen)
    res = resumen.como_dict()
    registrar_evento(
        "CARGA_ARCHIVO", u.usuario,
        f"{nombre}: {res['insertados']} insertados, {res['actualizados']} actualizados, {res['rechazados']} rechazados",
        request.client.host if request.client else None,
    )
    return res


@router.post("/peliculas")
async def cargar_peliculas(request: Request, archivo: UploadFile = File(...), u: Usuario = Depends(requiere_admin)):
    contenido = await _leer(archivo, (".dat", ".txt"))
    return await run_in_threadpool(_ejecutar, request, u, archivo.filename, lambda: peliculas.parsear(contenido), peliculas.cargar)


@router.post("/libros")
async def cargar_libros(request: Request, archivo: UploadFile = File(...), u: Usuario = Depends(requiere_admin)):
    contenido = await _leer(archivo, (".json",))
    return await run_in_threadpool(_ejecutar, request, u, archivo.filename, lambda: libros.parsear(contenido), libros.cargar)


@router.post("/nomina")
async def cargar_nomina(
    request: Request,
    archivo: UploadFile = File(...),
    anio: Annotated[int | None, Form()] = None,
    mes: Annotated[int | None, Form()] = None,
    u: Usuario = Depends(requiere_admin),
):
    contenido = await _leer(archivo, (".xlsx",))
    periodo = (anio, mes) if anio and mes else None
    if periodo and not (1 <= mes <= 12 and 1990 <= anio <= 2100):
        raise HTTPException(422, "Periodo invalido")
    return await run_in_threadpool(_ejecutar, request, u, archivo.filename, lambda: nomina.parsear(contenido, periodo), nomina.cargar)
