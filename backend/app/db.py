"""Acceso a datos con PyMySQL y SQL escrito a mano (RNF-01, RNF-08).

Toda consulta usa parametros (%s): nunca se concatena texto del usuario en el SQL.
Cada conexion fija @app_user para que los triggers sepan que usuario hizo el cambio.
"""
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pymysql
from pymysql.cursors import DictCursor

from .config import settings


def _conectar() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


@contextmanager
def conexion(usuario_app: str | None = None) -> Iterator[pymysql.connections.Connection]:
    """Abre una conexion, fija @app_user y hace commit o rollback al salir."""
    con = _conectar()
    try:
        with con.cursor() as cur:
            cur.execute("SET @app_user = %s", (usuario_app or "ANONIMO",))
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def consultar(sql: str, params: tuple | dict | None = None, usuario: str | None = None) -> list[dict[str, Any]]:
    with conexion(usuario) as con, con.cursor() as cur:
        cur.execute(sql, params)
        return list(cur.fetchall())


def consultar_uno(sql: str, params: tuple | dict | None = None, usuario: str | None = None) -> dict[str, Any] | None:
    filas = consultar(sql, params, usuario)
    return filas[0] if filas else None


def ejecutar(sql: str, params: tuple | dict | None = None, usuario: str | None = None) -> tuple[int, int]:
    """Ejecuta INSERT/UPDATE/DELETE. Devuelve (filas afectadas, ultimo id)."""
    with conexion(usuario) as con, con.cursor() as cur:
        n = cur.execute(sql, params)
        return n, cur.lastrowid
