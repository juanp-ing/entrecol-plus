"""Consultas de los cinco grupos de reportes + auditoria (RF-12, RF-13, RF-17).

SQL escrito a mano y parametrizado (RNF-01, RNF-08). Solo la direccion del orden (ASC/DESC)
se interpola, y sale de una lista blanca.

Cada reporte devuelve un diccionario neutro que pintan igual la pantalla (Chart.js) y el PDF:
  {"titulo", "parametros", "secciones": [kpi | tabla | grafico]}
"""
from collections import OrderedDict
from datetime import date

from ..db import consultar, consultar_uno

LIMITE_LISTA = 1000  # filas maximas por tabla en pantalla/PDF (los conteos siempre son completos)


def direccion(orden: str) -> str:
    return "DESC" if str(orden).lower().startswith("desc") else "ASC"


def kpi(*items: tuple[str, object]) -> dict:
    return {"tipo": "kpi", "items": [{"etiqueta": e, "valor": v} for e, v in items]}


def tabla(titulo: str, columnas: list[str], filas: list, nota: str | None = None) -> dict:
    total = len(filas)
    if total > LIMITE_LISTA:
        nota = (nota + " " if nota else "") + f"Se muestran {LIMITE_LISTA} de {total} filas."
        filas = filas[:LIMITE_LISTA]
    return {"tipo": "tabla", "titulo": titulo, "columnas": columnas, "filas": filas, "nota": nota}


def grafico(titulo: str, tipo: str, etiquetas: list, series: list[dict], apilado: bool = False) -> dict:
    return {"tipo": "grafico", "titulo": titulo, "grafico": tipo, "etiquetas": etiquetas,
            "series": series, "apilado": apilado}


def _matriz(filas: list[dict], fila: str, col: str, valor: str = "n") -> tuple[list, list[dict]]:
    """Convierte (fila, col, n) en etiquetas + una serie por columna, para barras comparativas."""
    etiquetas = list(OrderedDict.fromkeys(f[fila] for f in filas))
    columnas = sorted({f[col] for f in filas})
    idx = {(f[fila], f[col]): int(f[valor]) for f in filas}
    return etiquetas, [{"nombre": c, "datos": [idx.get((e, c), 0) for e in etiquetas]} for c in columnas]


NOMBRE = "CONCAT_WS(' ', e.primer_apellido, e.segundo_apellido, e.nombres)"


def _orden_nombre(d: str) -> str:
    return f"e.primer_apellido {d}, e.segundo_apellido {d}, e.nombres {d}"


# --------------------------------------------------------------------------- 1. Nomina
def reporte_nomina(orden: str, usuario: str) -> dict:
    d = direccion(orden)
    empleados = consultar(
        f"""SELECT e.codigo_empleado, {NOMBRE} AS nombre, dp.nombre_dependencia, c.nombre_cargo
              FROM empleado e
              JOIN dependencia dp ON dp.id_dependencia = e.id_dependencia
              JOIN cargo c        ON c.id_cargo = e.id_cargo
             ORDER BY {_orden_nombre(d)}""", usuario=usuario)
    por_dep = consultar(
        """SELECT dp.nombre_dependencia AS dependencia, COUNT(e.codigo_empleado) AS n
             FROM dependencia dp
             LEFT JOIN empleado e ON e.id_dependencia = dp.id_dependencia
            GROUP BY dp.id_dependencia, dp.nombre_dependencia
            ORDER BY dp.nombre_dependencia ASC""", usuario=usuario)
    lista_dep = consultar(
        f"""SELECT dp.nombre_dependencia, e.codigo_empleado, {NOMBRE} AS nombre
              FROM empleado e
              JOIN dependencia dp ON dp.id_dependencia = e.id_dependencia
             ORDER BY dp.nombre_dependencia ASC, {_orden_nombre(d)}""", usuario=usuario)
    dep_cargo = consultar(
        """SELECT dp.nombre_dependencia AS dependencia, c.nombre_cargo AS cargo, COUNT(*) AS n
             FROM empleado e
             JOIN dependencia dp ON dp.id_dependencia = e.id_dependencia
             JOIN cargo c        ON c.id_cargo = e.id_cargo
            GROUP BY dp.nombre_dependencia, c.nombre_cargo
            ORDER BY dp.nombre_dependencia ASC, c.nombre_cargo ASC""", usuario=usuario)
    lista_dep_cargo = consultar(
        f"""SELECT dp.nombre_dependencia, c.nombre_cargo, e.codigo_empleado, {NOMBRE} AS nombre
              FROM empleado e
              JOIN dependencia dp ON dp.id_dependencia = e.id_dependencia
              JOIN cargo c        ON c.id_cargo = e.id_cargo
             ORDER BY dp.nombre_dependencia ASC, c.nombre_cargo ASC, {_orden_nombre(d)}""", usuario=usuario)
    etq, series = _matriz(dep_cargo, "dependencia", "cargo")
    return {
        "titulo": "Reporte de nomina",
        "parametros": {"Orden de nombres": d},
        "secciones": [
            kpi(("Empleados", len(empleados)), ("Dependencias", len(por_dep)),
                ("Cargos", len({f["cargo"] for f in dep_cargo}))),
            tabla("Empleados de la empresa", ["Codigo", "Nombre", "Dependencia", "Cargo"],
                  [list(f.values()) for f in empleados]),
            grafico("Empleados por dependencia", "pie", [f["dependencia"] for f in por_dep],
                    [{"nombre": "Empleados", "datos": [int(f["n"]) for f in por_dep]}]),
            tabla("Cantidad por dependencia", ["Dependencia", "Empleados"], [[f["dependencia"], f["n"]] for f in por_dep]),
            tabla("Empleados por dependencia", ["Dependencia", "Codigo", "Nombre"], [list(f.values()) for f in lista_dep]),
            grafico("Empleados por dependencia y cargo", "bar", etq, series),
            tabla("Cantidad por dependencia y cargo", ["Dependencia", "Cargo", "Empleados"],
                  [[f["dependencia"], f["cargo"], f["n"]] for f in dep_cargo]),
            tabla("Empleados por dependencia y cargo", ["Dependencia", "Cargo", "Codigo", "Nombre"],
                  [list(f.values()) for f in lista_dep_cargo]),
        ],
    }


# --------------------------------------------------------------------------- 2. Informacion personal
def reporte_personal(codigo: int, usuario: str) -> dict:
    e = consultar_uno(
        f"""SELECT e.codigo_empleado, {NOMBRE} AS nombre, dp.nombre_dependencia, c.nombre_cargo,
                   DATE_FORMAT(e.fecha_ingreso, '%%d/%%m/%%Y') AS fecha_ingreso,
                   s.nombre_eps, a.nombre_arl, f.nombre_fondo, e.salario,
                   ROUND(e.salario * COALESCE(
                     (SELECT valor FROM parametro_nomina WHERE clave = 'PORC_APORTE_PENSION_EMPLEADO'), 0), 2)
                     AS aporte_pension
              FROM empleado e
              JOIN dependencia dp  ON dp.id_dependencia = e.id_dependencia
              JOIN cargo c         ON c.id_cargo = e.id_cargo
              JOIN eps s           ON s.id_eps = e.id_eps
              JOIN arl a           ON a.id_arl = e.id_arl
              JOIN fondo_pension f ON f.id_fondo_pension = e.id_fondo_pension
             WHERE e.codigo_empleado = %s""", (codigo,), usuario)
    if not e:
        return {"titulo": "Informacion personal", "parametros": {"Codigo": codigo},
                "secciones": [kpi(("Resultado", "No existe un empleado con ese codigo"))]}
    novedades = consultar(
        """SELECT CONCAT(LPAD(p.mes, 2, '0'), '/', p.anio) AS periodo, t.nombre_tipo,
                  DATE_FORMAT(v.fecha_inicio, '%%d/%%m/%%Y') AS inicio,
                  DATE_FORMAT(v.fecha_fin, '%%d/%%m/%%Y') AS fin, v.dias
             FROM novedad v
             JOIN tipo_novedad t   ON t.id_tipo_novedad = v.id_tipo_novedad
             JOIN nomina_mensual n ON n.id_nomina = v.id_nomina
             JOIN periodo p        ON p.id_periodo = n.id_periodo
            WHERE n.codigo_empleado = %s
            ORDER BY v.fecha_inicio ASC""", (codigo,), usuario)
    liquidaciones = consultar(
        """SELECT CONCAT(LPAD(p.mes, 2, '0'), '/', p.anio) AS periodo, n.dias_trabajados, n.bonificacion, n.transporte
             FROM nomina_mensual n JOIN periodo p ON p.id_periodo = n.id_periodo
            WHERE n.codigo_empleado = %s
            ORDER BY p.anio ASC, p.mes ASC""", (codigo,), usuario)
    return {
        "titulo": "Informacion personal",
        "parametros": {"Codigo": codigo},
        "secciones": [
            tabla("Datos del empleado", ["Campo", "Valor"], [
                ["Nombre completo", e["nombre"]], ["Codigo", e["codigo_empleado"]],
                ["Dependencia", e["nombre_dependencia"]], ["Cargo", e["nombre_cargo"]],
                ["Fecha de ingreso", e["fecha_ingreso"]], ["EPS", e["nombre_eps"]], ["ARL", e["nombre_arl"]],
                ["Fondo de pension", e["nombre_fondo"]], ["Aporte a pension", e["aporte_pension"]],
                ["Salario", e["salario"]],
            ]),
            tabla("Liquidaciones", ["Periodo", "Dias trabajados", "Bonificacion", "Transporte"],
                  [list(f.values()) for f in liquidaciones]),
            tabla("Discriminacion de novedades", ["Periodo", "Tipo", "Inicio", "Fin", "Dias"],
                  [list(f.values()) for f in novedades], None if novedades else "El empleado no tiene novedades."),
        ],
    }


# --------------------------------------------------------------------------- 3. Salud y pension
def _frecuencia(tabla_cat: str, pk: str, col: str, usuario: str) -> list[dict]:
    # tabla_cat/pk/col son constantes de este modulo, no texto del usuario
    return consultar(
        f"""SELECT x.{col} AS nombre, COUNT(e.codigo_empleado) AS n
              FROM {tabla_cat} x LEFT JOIN empleado e ON e.{pk} = x.{pk}
             GROUP BY x.{pk}, x.{col}
             ORDER BY x.{col} ASC""", usuario=usuario)


def _cruce_dep(tabla_cat: str, pk: str, col: str, usuario: str) -> list[dict]:
    return consultar(
        f"""SELECT x.{col} AS cat, dp.nombre_dependencia AS dependencia, COUNT(*) AS n
              FROM empleado e
              JOIN {tabla_cat} x  ON x.{pk} = e.{pk}
              JOIN dependencia dp ON dp.id_dependencia = e.id_dependencia
             GROUP BY x.{col}, dp.nombre_dependencia
             ORDER BY x.{col} ASC, dp.nombre_dependencia ASC""", usuario=usuario)


def _cargo_cat(tabla_cat: str, pk: str, col: str, d: str, usuario: str) -> tuple[list, list]:
    conteo = consultar(
        f"""SELECT c.nombre_cargo, x.{col} AS cat, COUNT(*) AS n
              FROM empleado e
              JOIN cargo c       ON c.id_cargo = e.id_cargo
              JOIN {tabla_cat} x ON x.{pk} = e.{pk}
             GROUP BY c.nombre_cargo, x.{col}
             ORDER BY c.nombre_cargo ASC, x.{col} ASC""", usuario=usuario)
    lista = consultar(
        f"""SELECT c.nombre_cargo, x.{col} AS cat, e.codigo_empleado, {NOMBRE} AS nombre
              FROM empleado e
              JOIN cargo c       ON c.id_cargo = e.id_cargo
              JOIN {tabla_cat} x ON x.{pk} = e.{pk}
             ORDER BY c.nombre_cargo ASC, x.{col} ASC, {_orden_nombre(d)}""", usuario=usuario)
    return conteo, lista


def reporte_salud_pension(orden: str, usuario: str) -> dict:
    d = direccion(orden)
    secciones = []
    for etiqueta, tabla_cat, pk, col in (("EPS", "eps", "id_eps", "nombre_eps"),
                                          ("Fondo de pension", "fondo_pension", "id_fondo_pension", "nombre_fondo")):
        frec = _frecuencia(tabla_cat, pk, col, usuario)
        cruce = _cruce_dep(tabla_cat, pk, col, usuario)
        etq, series = _matriz(cruce, "cat", "dependencia")
        conteo, lista = _cargo_cat(tabla_cat, pk, col, d, usuario)
        secciones += [
            grafico(f"Frecuencia de empleados por {etiqueta}", "bar", [f["nombre"] for f in frec],
                    [{"nombre": "Empleados", "datos": [int(f["n"]) for f in frec]}]),
            grafico(f"{etiqueta} por dependencia", "bar", etq, series),
            tabla(f"Cantidad por cargo y {etiqueta}", ["Cargo", etiqueta, "Empleados"],
                  [list(f.values()) for f in conteo]),
            tabla(f"Empleados por cargo y {etiqueta}", ["Cargo", etiqueta, "Codigo", "Nombre"],
                  [list(f.values()) for f in lista]),
        ]
    return {"titulo": "Reporte de salud y pension", "parametros": {"Orden de nombres": d}, "secciones": secciones}


# --------------------------------------------------------------------------- 4. Novedades
def reporte_novedades(desde: date, hasta: date, orden: str, usuario: str) -> dict:
    """desde/hasta: primer dia del mes inicial y ultimo dia del mes final (filtro MM/AAAA)."""
    d = direccion(orden)
    rango = (hasta, desde)  # una novedad cae en el rango si se solapa con el
    filtro = "v.fecha_inicio <= %s AND v.fecha_fin >= %s"
    lista = consultar(
        f"""SELECT e.codigo_empleado, {NOMBRE} AS nombre, dp.nombre_dependencia, c.nombre_cargo, t.nombre_tipo,
                   DATE_FORMAT(v.fecha_inicio, '%%d/%%m/%%Y') AS inicio,
                   DATE_FORMAT(v.fecha_fin, '%%d/%%m/%%Y') AS fin, v.dias
              FROM novedad v
              JOIN tipo_novedad t   ON t.id_tipo_novedad = v.id_tipo_novedad
              JOIN nomina_mensual n ON n.id_nomina = v.id_nomina
              JOIN empleado e       ON e.codigo_empleado = n.codigo_empleado
              JOIN dependencia dp   ON dp.id_dependencia = e.id_dependencia
              JOIN cargo c          ON c.id_cargo = e.id_cargo
             WHERE {filtro}
             ORDER BY {_orden_nombre(d)}, v.fecha_inicio ASC""", rango, usuario)
    por_dep = consultar(
        f"""SELECT dp.nombre_dependencia AS nombre, COUNT(DISTINCT e.codigo_empleado) AS n
              FROM novedad v
              JOIN nomina_mensual n ON n.id_nomina = v.id_nomina
              JOIN empleado e       ON e.codigo_empleado = n.codigo_empleado
              JOIN dependencia dp   ON dp.id_dependencia = e.id_dependencia
             WHERE {filtro}
             GROUP BY dp.nombre_dependencia
             ORDER BY dp.nombre_dependencia ASC""", rango, usuario)
    por_cargo = consultar(
        f"""SELECT c.nombre_cargo AS nombre, COUNT(DISTINCT e.codigo_empleado) AS n
              FROM novedad v
              JOIN nomina_mensual n ON n.id_nomina = v.id_nomina
              JOIN empleado e       ON e.codigo_empleado = n.codigo_empleado
              JOIN cargo c          ON c.id_cargo = e.id_cargo
             WHERE {filtro}
             GROUP BY c.nombre_cargo
             ORDER BY c.nombre_cargo ASC""", rango, usuario)
    return {
        "titulo": "Reporte de novedades",
        "parametros": {"Desde": desde.strftime("%m/%Y"), "Hasta": hasta.strftime("%m/%Y"), "Orden de nombres": d},
        "secciones": [
            kpi(("Empleados con novedades", len({f["codigo_empleado"] for f in lista})), ("Novedades", len(lista))),
            tabla("Empleados con novedades", ["Codigo", "Nombre", "Dependencia", "Cargo", "Tipo", "Inicio", "Fin", "Dias"],
                  [list(f.values()) for f in lista]),
            grafico("Empleados con novedades por dependencia", "bar", [f["nombre"] for f in por_dep],
                    [{"nombre": "Empleados", "datos": [int(f["n"]) for f in por_dep]}]),
            tabla("Cantidad por dependencia", ["Dependencia", "Empleados"], [list(f.values()) for f in por_dep]),
            tabla("Cantidad por cargo", ["Cargo", "Empleados"], [list(f.values()) for f in por_cargo]),
        ],
    }


# --------------------------------------------------------------------------- 5. Entretenimiento
def reporte_entretenimiento(anio_desde: int, anio_hasta: int, n_top: int, n_generos: int,
                            orden: str, usuario: str) -> dict:
    d = direccion(orden)
    rango = (anio_desde, anio_hasta)
    pel_genero = consultar(
        f"""SELECT g.nombre_genero, p.titulo, p.anio
              FROM pelicula p
              JOIN pelicula_genero pg ON pg.id_pelicula = p.id_pelicula
              JOIN genero g           ON g.id_genero = pg.id_genero
             WHERE p.anio BETWEEN %s AND %s
             ORDER BY g.nombre_genero ASC, p.titulo {d}""", rango, usuario)
    frec_genero = consultar(
        """SELECT g.nombre_genero AS nombre, COUNT(pg.id_pelicula) AS n
             FROM genero g
             LEFT JOIN pelicula_genero pg ON pg.id_genero = g.id_genero
             LEFT JOIN pelicula p         ON p.id_pelicula = pg.id_pelicula AND p.anio BETWEEN %s AND %s
            WHERE p.id_pelicula IS NOT NULL
            GROUP BY g.id_genero, g.nombre_genero
            ORDER BY g.nombre_genero ASC""", rango, usuario)
    con_n_generos = consultar(
        f"""SELECT p.id_pelicula, p.titulo, p.anio, COUNT(pg.id_genero) AS generos
              FROM pelicula p
              LEFT JOIN pelicula_genero pg ON pg.id_pelicula = p.id_pelicula
             GROUP BY p.id_pelicula, p.titulo, p.anio
            HAVING COUNT(pg.id_genero) = %s
             ORDER BY p.titulo {d}""", (n_generos,), usuario)
    top_n = consultar(
        """SELECT l.titulo, YEAR(l.fecha_publicacion) AS anio, l.rating_promedio, l.cantidad_ratings
             FROM libro l
            WHERE l.rating_promedio IS NOT NULL AND l.cantidad_ratings > 0
            ORDER BY l.rating_promedio DESC, l.cantidad_ratings DESC, l.titulo ASC
            LIMIT %s""", (n_top,), usuario)
    top5_anio = consultar(
        """WITH clasificados AS (
               SELECT YEAR(l.fecha_publicacion) AS anio, l.titulo, l.rating_promedio, l.cantidad_ratings,
                      ROW_NUMBER() OVER (PARTITION BY YEAR(l.fecha_publicacion)
                                         ORDER BY l.rating_promedio DESC, l.cantidad_ratings DESC) AS mejor,
                      ROW_NUMBER() OVER (PARTITION BY YEAR(l.fecha_publicacion)
                                         ORDER BY l.rating_promedio ASC, l.cantidad_ratings DESC) AS peor
                 FROM libro l
                WHERE l.fecha_publicacion IS NOT NULL AND l.cantidad_ratings > 0
                  AND YEAR(l.fecha_publicacion) BETWEEN %s AND %s)
           SELECT anio, CASE WHEN mejor <= 5 THEN 'Mejor' ELSE 'Peor' END AS grupo,
                  CASE WHEN mejor <= 5 THEN mejor ELSE peor END AS puesto,
                  titulo, rating_promedio, cantidad_ratings
             FROM clasificados
            WHERE mejor <= 5 OR peor <= 5
            ORDER BY anio ASC, grupo ASC, puesto ASC""", rango, usuario)
    libros_anio = consultar(
        """SELECT YEAR(l.fecha_publicacion) AS anio, COUNT(*) AS n
             FROM libro l
            WHERE YEAR(l.fecha_publicacion) BETWEEN %s AND %s
            GROUP BY YEAR(l.fecha_publicacion)
            ORDER BY anio ASC""", rango, usuario)
    return {
        "titulo": "Reporte de la base de entretenimiento",
        "parametros": {"Anos": f"{anio_desde} - {anio_hasta}", "Top N": n_top, "N generos": n_generos,
                       "Orden de titulos": d},
        "secciones": [
            kpi(("Peliculas en el rango", len({(f["titulo"], f["anio"]) for f in pel_genero})),
                (f"Peliculas con {n_generos} generos", len(con_n_generos))),
            grafico("Frecuencia de peliculas por genero", "bar", [f["nombre"] for f in frec_genero],
                    [{"nombre": "Peliculas", "datos": [int(f["n"]) for f in frec_genero]}]),
            tabla("Peliculas por genero", ["Genero", "Titulo", "Ano"], [list(f.values()) for f in pel_genero]),
            tabla(f"Top {n_top} de libros con mejor calificacion", ["Titulo", "Ano", "Calificacion", "Calificaciones"],
                  [list(f.values()) for f in top_n]),
            tabla("Top 5 de libros con mejor y peor calificacion por ano",
                  ["Ano", "Grupo", "Puesto", "Titulo", "Calificacion", "Calificaciones"],
                  [list(f.values()) for f in top5_anio]),
            tabla(f"Peliculas con {n_generos} generos", ["ID", "Titulo", "Ano", "Generos"],
                  [list(f.values()) for f in con_n_generos]),
            grafico("Frecuencia de libros por ano de publicacion", "bar", [str(f["anio"]) for f in libros_anio],
                    [{"nombre": "Libros", "datos": [int(f["n"]) for f in libros_anio]}]),
        ],
    }


# --------------------------------------------------------------------------- Auditoria (solo admin)
def reporte_auditoria(desde: date, hasta: date, usuario_filtro: str, usuario: str) -> dict:
    params = (desde, hasta, usuario_filtro, usuario_filtro)
    eventos = consultar(
        """SELECT DATE_FORMAT(fecha, '%%d/%%m/%%Y %%H:%%i:%%s') AS fecha, tipo, usuario_app, detalle, ip
             FROM auditoria_evento
            WHERE fecha >= %s AND fecha < DATE_ADD(%s, INTERVAL 1 DAY)
              AND (%s = '' OR usuario_app = %s)
            ORDER BY id_evento DESC
            LIMIT 2000""", params, usuario)
    cambios = consultar(
        """SELECT DATE_FORMAT(fecha, '%%d/%%m/%%Y %%H:%%i:%%s') AS fecha, usuario_app, tabla, operacion, llave,
                  LEFT(COALESCE(valores_antes, ''), 300) AS antes, LEFT(COALESCE(valores_despues, ''), 300) AS despues
             FROM auditoria_datos
            WHERE fecha >= %s AND fecha < DATE_ADD(%s, INTERVAL 1 DAY)
              AND (%s = '' OR usuario_app = %s)
            ORDER BY id_auditoria DESC
            LIMIT 2000""", params, usuario)
    por_tipo = consultar(
        """SELECT tipo AS nombre, COUNT(*) AS n FROM auditoria_evento
            WHERE fecha >= %s AND fecha < DATE_ADD(%s, INTERVAL 1 DAY) AND (%s = '' OR usuario_app = %s)
            GROUP BY tipo ORDER BY tipo ASC""", params, usuario)
    por_tabla = consultar(
        """SELECT tabla, operacion, COUNT(*) AS n FROM auditoria_datos
            WHERE fecha >= %s AND fecha < DATE_ADD(%s, INTERVAL 1 DAY) AND (%s = '' OR usuario_app = %s)
            GROUP BY tabla, operacion ORDER BY tabla ASC""", params, usuario)
    etq, series = _matriz(por_tabla, "tabla", "operacion")
    return {
        "titulo": "Reporte de auditoria",
        "parametros": {"Desde": desde.strftime("%d/%m/%Y"), "Hasta": hasta.strftime("%d/%m/%Y"),
                       "Usuario": usuario_filtro or "Todos"},
        "secciones": [
            kpi(("Eventos", sum(int(f["n"]) for f in por_tipo)), ("Cambios de datos", sum(int(f["n"]) for f in por_tabla))),
            grafico("Eventos por tipo", "pie", [f["nombre"] for f in por_tipo],
                    [{"nombre": "Eventos", "datos": [int(f["n"]) for f in por_tipo]}]),
            grafico("Cambios por tabla y operacion", "bar", etq, series, apilado=True),
            tabla("Eventos (inicios de sesion, accesos, reportes, cargas)", ["Fecha", "Tipo", "Usuario", "Detalle", "IP"],
                  [list(f.values()) for f in eventos]),
            tabla("Cambios de datos (triggers)", ["Fecha", "Usuario", "Tabla", "Operacion", "Llave", "Antes", "Despues"],
                  [list(f.values()) for f in cambios]),
        ],
    }
