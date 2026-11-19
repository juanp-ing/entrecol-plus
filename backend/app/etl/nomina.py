"""Carga de empleados, liquidaciones y novedades desde el libro de Excel (RF-05).

Hoja 1: informacion general de empleados.  Hojas 2..n: liquidacion y novedades de un mes cada una.
Transformaciones: separar catalogos (dependencia, cargo, EPS, ARL, pension), partir el nombre en
apellidos y nombres, convertir la fecha AAAAMMDD y crear un periodo por cada hoja de liquidacion.

Periodo de cada hoja: si el nombre de la hoja trae AAAA-MM o MM-AAAA se usa ese; si no, el periodo
indicado al cargar; si no se indico, el mes de la novedad mas antigua de la hoja (queda como aviso).
"""
import io
import re
import unicodedata
from datetime import date, datetime

import pandas as pd

from .comun import ErrorEstructura, Resumen, id_catalogo

COLS_EMPLEADO = ["CODIGO", "NOMBRE DEL EMPLEADO", "DEPENDENCIA", "CARGO", "FECHA INGRESO",
                 "EPS", "ARL", "PENSION", "SUELDO"]
COLS_LIQUIDACION = [
    "CODIGO", "NOVEDAD INCAPACIDAD", "NOVEDAD VACACIONES", "NUMERO DIAS TRABAJADOS EN EL MES",
    "NUMERO DIAS INCAPACIDADES EN EL MES", "NUMERO DE DIAS VACACIONES", "FECHA DE INICIO DE VACACIONES",
    "FECHA TERMINACION DE VACACIONES", "FECHA INICIO INCAPACIDAD", "FECHA TERMINACION INCAPACIDAD",
    "BONIFICACION", "TRANSPORTE",
]
_RE_PERIODO = [re.compile(r"(?P<a>(19|20)\d{2})\D(?P<m>\d{1,2})"), re.compile(r"(?P<m>\d{1,2})\D(?P<a>(19|20)\d{2})")]


def _norm(txt) -> str:
    s = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def _validar_columnas(df: pd.DataFrame, esperadas: list[str], hoja: str) -> pd.DataFrame:
    df = df.rename(columns={c: _norm(c) for c in df.columns})
    faltan = [c for c in esperadas if c not in df.columns]
    if faltan:
        raise ErrorEstructura(f"Hoja '{hoja}': faltan columnas {', '.join(faltan)}")
    return df.dropna(how="all")


def _vacio(v) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and not v.strip())


def _fecha(v) -> date | None:
    if _vacio(v):
        return None
    if isinstance(v, (datetime, pd.Timestamp)):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(int(v)) if isinstance(v, (int, float)) else str(v).strip()
    if re.fullmatch(r"\d{8}", s):  # AAAAMMDD
        return date(int(s[:4]), int(s[4:6]), int(s[6:]))
    return pd.to_datetime(s, dayfirst=True).date()


def _partir_nombre(nombre: str) -> tuple[str, str | None, str]:
    p = nombre.split()
    if len(p) >= 4:
        return p[0], p[1], " ".join(p[2:])
    if len(p) == 3:
        return p[0], p[1], p[2]
    if len(p) == 2:
        return p[0], None, p[1]
    raise ValueError(f"nombre incompleto: {nombre!r}")


def _periodo_de_hoja(nombre: str) -> tuple[int, int] | None:
    for rx in _RE_PERIODO:
        m = rx.search(nombre)
        if m and 1 <= int(m["m"]) <= 12:
            return int(m["a"]), int(m["m"])
    return None


def parsear(contenido: bytes, periodo: tuple[int, int] | None = None) -> tuple[dict, Resumen]:
    r = Resumen("nomina")
    try:
        hojas = pd.read_excel(io.BytesIO(contenido), sheet_name=None, engine="openpyxl", dtype=object)
    except Exception as exc:
        raise ErrorEstructura(f"No se pudo leer el libro de Excel: {exc}")
    if len(hojas) < 2:
        raise ErrorEstructura("El libro debe tener la hoja de empleados y al menos una hoja de liquidacion")
    nombres = list(hojas)

    emp_df = _validar_columnas(hojas[nombres[0]], COLS_EMPLEADO, nombres[0])
    empleados: dict[int, dict] = {}
    for i, f in enumerate(emp_df.to_dict("records"), start=2):
        r.leidos += 1
        try:
            cod = int(f["CODIGO"])
            ap1, ap2, nom = _partir_nombre(_norm(f["NOMBRE DEL EMPLEADO"]))
            ingreso = _fecha(f["FECHA INGRESO"])
            salario = float(f["SUELDO"])
            if salario <= 0:
                raise ValueError("salario debe ser mayor que cero")
            catalogos = {k: str(f[k]).strip() for k in ("DEPENDENCIA", "CARGO", "EPS", "ARL", "PENSION")}
            if not ingreso or any(not v or v == "nan" for v in catalogos.values()):
                raise ValueError("faltan datos obligatorios")
        except (TypeError, ValueError) as exc:
            r.rechazar(f"{nombres[0]} fila {i}", str(exc))
            continue
        if cod in empleados:
            r.rechazar(f"{nombres[0]} fila {i}", f"Codigo de empleado repetido: {cod}")
            continue
        empleados[cod] = {"codigo": cod, "ap1": ap1, "ap2": ap2, "nombres": nom,
                          "ingreso": ingreso, "salario": salario, **catalogos}

    liquidaciones = []
    for hoja in nombres[1:]:
        df = _validar_columnas(hojas[hoja], COLS_LIQUIDACION, hoja)
        filas = []
        for i, f in enumerate(df.to_dict("records"), start=2):
            r.leidos += 1
            ref = f"{hoja} fila {i}"
            try:
                cod = int(f["CODIGO"])
                if cod not in empleados:
                    raise ValueError(f"el empleado {cod} no existe en la hoja de empleados")
                novs = []
                if not _vacio(f["NOVEDAD INCAPACIDAD"]):
                    novs.append(("INCAPACIDAD", _fecha(f["FECHA INICIO INCAPACIDAD"]),
                                 _fecha(f["FECHA TERMINACION INCAPACIDAD"]), int(f["NUMERO DIAS INCAPACIDADES EN EL MES"])))
                if not _vacio(f["NOVEDAD VACACIONES"]):
                    novs.append(("VACACIONES", _fecha(f["FECHA DE INICIO DE VACACIONES"]),
                                 _fecha(f["FECHA TERMINACION DE VACACIONES"]), int(f["NUMERO DE DIAS VACACIONES"])))
                for tipo, ini, fin, dias in novs:
                    if not ini or not fin or fin < ini:
                        raise ValueError(f"fechas de {tipo.lower()} incompletas o invertidas")
                    if not 1 <= dias <= 31:
                        raise ValueError(f"dias de {tipo.lower()} fuera de rango: {dias}")
                dias_trab = int(f["NUMERO DIAS TRABAJADOS EN EL MES"])
                if not 0 <= dias_trab <= 30:
                    raise ValueError(f"dias trabajados fuera de rango: {dias_trab}")
                filas.append({
                    "codigo": cod, "dias": dias_trab,
                    "bonificacion": 0.0 if _vacio(f["BONIFICACION"]) else float(f["BONIFICACION"]),
                    "transporte": 0.0 if _vacio(f["TRANSPORTE"]) else float(f["TRANSPORTE"]),
                    "novedades": novs,
                })
            except (TypeError, ValueError) as exc:
                r.rechazar(ref, str(exc))

        per = _periodo_de_hoja(hoja) or periodo
        if per is None:
            inicios = [n[1] for fl in filas for n in fl["novedades"]]
            if not inicios:
                raise ErrorEstructura(f"Hoja '{hoja}': no se puede deducir el periodo; indiquelo al cargar")
            primero = min(inicios)
            per = (primero.year, primero.month)
            r.avisos.append(f"Hoja '{hoja}': periodo {per[1]:02d}/{per[0]} deducido de la novedad mas antigua")
        liquidaciones.append({"hoja": hoja, "periodo": per, "filas": filas})

    return {"empleados": list(empleados.values()), "liquidaciones": liquidaciones}, r


def cargar(cur, datos: dict, r: Resumen) -> None:
    caches: dict[str, dict] = {k: {} for k in ("dep", "car", "eps", "arl", "pen", "tipo")}
    for e in datos["empleados"]:
        ids = (
            id_catalogo(cur, caches["dep"], "dependencia", "id_dependencia", "nombre_dependencia", e["DEPENDENCIA"]),
            id_catalogo(cur, caches["car"], "cargo", "id_cargo", "nombre_cargo", e["CARGO"]),
            id_catalogo(cur, caches["eps"], "eps", "id_eps", "nombre_eps", e["EPS"]),
            id_catalogo(cur, caches["arl"], "arl", "id_arl", "nombre_arl", e["ARL"]),
            id_catalogo(cur, caches["pen"], "fondo_pension", "id_fondo_pension", "nombre_fondo", e["PENSION"]),
        )
        n = cur.execute(
            """INSERT INTO empleado (codigo_empleado, primer_apellido, segundo_apellido, nombres, fecha_ingreso,
                                     salario, id_dependencia, id_cargo, id_eps, id_arl, id_fondo_pension)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE primer_apellido = VALUES(primer_apellido),
                 segundo_apellido = VALUES(segundo_apellido), nombres = VALUES(nombres),
                 fecha_ingreso = VALUES(fecha_ingreso), salario = VALUES(salario),
                 id_dependencia = VALUES(id_dependencia), id_cargo = VALUES(id_cargo), id_eps = VALUES(id_eps),
                 id_arl = VALUES(id_arl), id_fondo_pension = VALUES(id_fondo_pension)""",
            (e["codigo"], e["ap1"], e["ap2"], e["nombres"], e["ingreso"], e["salario"], *ids),
        )
        r.contar(n)

    for liq in datos["liquidaciones"]:
        anio, mes = liq["periodo"]
        cur.execute("INSERT IGNORE INTO periodo (anio, mes) VALUES (%s, %s)", (anio, mes))
        cur.execute("SELECT id_periodo FROM periodo WHERE anio = %s AND mes = %s", (anio, mes))
        id_per = cur.fetchone()["id_periodo"]
        for f in liq["filas"]:
            n = cur.execute(
                """INSERT INTO nomina_mensual (codigo_empleado, id_periodo, dias_trabajados, bonificacion, transporte)
                   VALUES (%s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE dias_trabajados = VALUES(dias_trabajados),
                     bonificacion = VALUES(bonificacion), transporte = VALUES(transporte)""",
                (f["codigo"], id_per, f["dias"], f["bonificacion"], f["transporte"]),
            )
            r.contar(n)
            cur.execute("SELECT id_nomina FROM nomina_mensual WHERE codigo_empleado = %s AND id_periodo = %s",
                        (f["codigo"], id_per))
            id_nom = cur.fetchone()["id_nomina"]
            nuevas = {(id_nom, id_catalogo(cur, caches["tipo"], "tipo_novedad", "id_tipo_novedad", "nombre_tipo", t),
                       ini, fin, dias) for t, ini, fin, dias in f["novedades"]}
            cur.execute("SELECT id_nomina, id_tipo_novedad, fecha_inicio, fecha_fin, dias FROM novedad WHERE id_nomina = %s",
                        (id_nom,))
            if {tuple(x.values()) for x in cur.fetchall()} != nuevas:  # solo se reescriben si cambiaron
                cur.execute("DELETE FROM novedad WHERE id_nomina = %s", (id_nom,))
                cur.executemany(
                    "INSERT INTO novedad (id_nomina, id_tipo_novedad, fecha_inicio, fecha_fin, dias) VALUES (%s, %s, %s, %s, %s)",
                    list(nuevas))
