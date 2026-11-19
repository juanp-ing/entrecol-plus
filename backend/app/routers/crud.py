"""CRUD generico sobre las entidades declaradas en entidades.py (RF-11).

Lectura: cualquier usuario autenticado (salvo entidades admin_lectura).
Escritura: solo ADMINISTRADOR. Listados paginados (RNF-04).
"""
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import pymysql
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from ..db import conexion, consultar, consultar_uno
from ..entidades import ENTIDADES, Entidad
from ..seguridad import ADMIN, Usuario, hash_password, requiere_admin, usuario_actual

router = APIRouter(prefix="/api/crud", tags=["CRUD"])


def _entidad(clave: str, u: Usuario) -> Entidad:
    e = ENTIDADES.get(clave)
    if not e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Entidad desconocida: {clave}")
    if e.admin_lectura and u.rol != ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el administrador puede ver esta entidad")
    return e


def _pk_cols(e: Entidad) -> list[str]:
    return e.pk.split(",")


def _pk_valores(e: Entidad, id_: str) -> list[str]:
    partes = id_.split(",")
    if len(partes) != len(_pk_cols(e)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Identificador invalido")
    return partes


def _convertir(campo, valor: Any) -> Any:
    if valor in (None, ""):
        if campo.requerido and campo.tipo not in ("password", "bool"):
            raise HTTPException(422, f"El campo '{campo.etiqueta}' es obligatorio")
        return None
    try:
        match campo.tipo:
            case "entero":
                return int(valor)
            case "decimal":
                return Decimal(str(valor))
            case "fecha":
                return date.fromisoformat(str(valor)[:10])
            case "bool":
                return 1 if valor in (True, 1, "1", "true", "on") else 0
            case _:
                return str(valor).strip()
    except (ValueError, InvalidOperation):
        raise HTTPException(422, f"Valor invalido para '{campo.etiqueta}': {valor}")


def _preparar(e: Entidad, datos: dict, creando: bool) -> dict[str, Any]:
    fila: dict[str, Any] = {}
    for c in e.campos:
        if c.auto or (not creando and c.nombre in _pk_cols(e)):
            continue
        if c.tipo == "password":
            plano = datos.get(c.nombre) or ""
            if creando and len(plano) < 8:
                raise HTTPException(422, "La contrasena debe tener al menos 8 caracteres")
            if plano:
                if len(plano) < 8:
                    raise HTTPException(422, "La contrasena debe tener al menos 8 caracteres")
                fila["password_hash"] = hash_password(plano)
            continue
        if c.nombre not in datos and not creando:
            continue
        fila[c.nombre] = _convertir(c, datos.get(c.nombre))
    return fila


def _error_bd(exc: pymysql.MySQLError) -> HTTPException:
    codigo = exc.args[0] if exc.args else 0
    mensajes = {
        1062: "Ya existe un registro con ese valor unico",
        1451: "No se puede eliminar: otros registros dependen de este",
        1452: "El valor seleccionado en una relacion no existe",
        4025: "Un valor no cumple las restricciones de la tabla",
    }
    return HTTPException(status.HTTP_409_CONFLICT, mensajes.get(codigo, f"Error de base de datos ({codigo})"))


@router.get("")
def listar_entidades(u: Usuario = Depends(usuario_actual)):
    return [
        {
            "clave": e.clave, "titulo": e.titulo, "modulo": e.modulo, "pk": e.pk,
            "solo_lectura": e.extras.get("solo_lectura", False),
            "campos": [c.__dict__ for c in e.campos],
        }
        for e in ENTIDADES.values()
        if not (e.admin_lectura and u.rol != ADMIN)
    ]


@router.get("/{clave}")
def listar(
    clave: str,
    q: str = "",
    pagina: int = Query(1, ge=1),
    tam: int = Query(25, ge=1, le=500),
    u: Usuario = Depends(usuario_actual),
):
    e = _entidad(clave, u)
    where, params = "", []
    if q:
        where = f" WHERE {e.busqueda} LIKE %s"
        params.append(f"%{q}%")
    total = consultar_uno(f"SELECT COUNT(*) AS n FROM ({e.listado}{where}) t", tuple(params), u.usuario)["n"]
    filas = consultar(
        f"{e.listado}{where} ORDER BY {e.orden} LIMIT %s OFFSET %s",
        (*params, tam, (pagina - 1) * tam), u.usuario,
    )
    return {"total": total, "pagina": pagina, "tam": tam, "filas": filas}


@router.get("/{clave}/{id_}")
def obtener(clave: str, id_: str, u: Usuario = Depends(usuario_actual)):
    e = _entidad(clave, u)
    cols = _pk_cols(e)
    # El listado usa alias de tabla; se envuelve para filtrar por la llave real
    fila = consultar_uno(
        f"SELECT t.* FROM ({e.listado}) t WHERE " + " AND ".join(f"t.{c} = %s" for c in cols),
        tuple(_pk_valores(e, id_)), u.usuario,
    )
    if not fila:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Registro no encontrado")
    return fila


@router.post("/{clave}", status_code=201)
def crear(clave: str, datos: dict = Body(...), u: Usuario = Depends(requiere_admin)):
    e = _entidad(clave, u)
    if e.extras.get("solo_lectura"):
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED, "Entidad de solo lectura")
    fila = _preparar(e, datos, creando=True)
    cols = ", ".join(fila)
    marcas = ", ".join(["%s"] * len(fila))
    try:
        with conexion(u.usuario) as con, con.cursor() as cur:
            cur.execute(f"INSERT INTO {e.tabla} ({cols}) VALUES ({marcas})", tuple(fila.values()))
            nuevo = cur.lastrowid
    except pymysql.MySQLError as exc:
        raise _error_bd(exc)
    return {"ok": True, "id": nuevo or ",".join(str(fila.get(c)) for c in _pk_cols(e))}


@router.put("/{clave}/{id_}")
def actualizar(clave: str, id_: str, datos: dict = Body(...), u: Usuario = Depends(requiere_admin)):
    e = _entidad(clave, u)
    if e.extras.get("solo_lectura"):
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED, "Entidad de solo lectura")
    fila = _preparar(e, datos, creando=False)
    if not fila:
        raise HTTPException(422, "No hay cambios para guardar")
    sets = ", ".join(f"{c} = %s" for c in fila)
    cond = " AND ".join(f"{c} = %s" for c in _pk_cols(e))
    try:
        with conexion(u.usuario) as con, con.cursor() as cur:
            n = cur.execute(f"UPDATE {e.tabla} SET {sets} WHERE {cond}",
                            (*fila.values(), *_pk_valores(e, id_)))
    except pymysql.MySQLError as exc:
        raise _error_bd(exc)
    return {"ok": True, "afectados": n}


@router.delete("/{clave}/{id_}")
def eliminar(clave: str, id_: str, u: Usuario = Depends(requiere_admin)):
    e = _entidad(clave, u)
    if e.extras.get("solo_lectura"):
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED, "Entidad de solo lectura")
    if e.clave == "usuarios" and id_ == str(u.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "No puede eliminar su propio usuario")
    cond = " AND ".join(f"{c} = %s" for c in _pk_cols(e))
    try:
        with conexion(u.usuario) as con, con.cursor() as cur:
            n = cur.execute(f"DELETE FROM {e.tabla} WHERE {cond}", tuple(_pk_valores(e, id_)))
    except pymysql.MySQLError as exc:
        raise _error_bd(exc)
    if not n:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Registro no encontrado")
    return {"ok": True}
