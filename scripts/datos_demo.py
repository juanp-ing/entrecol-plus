"""Datos de demostracion para la presentacion: empleados, nomina abr-dic 2022, usuarios y auditoria.

Todos los cambios pasan por las tablas normales, asi que los triggers escriben auditoria_datos de verdad.
Para que el historial no quede todo con la fecha de hoy, cada accion fija la hora de la sesion
(SET timestamp) en un dia habil de las ultimas semanas; los eventos (logins, accesos, reportes,
cargas) se insertan en auditoria_evento con esas mismas fechas.

Uso (desde la raiz del proyecto):
    uv run python scripts/datos_demo.py
No se ejecuta dos veces: si el empleado 5021 ya existe, termina sin hacer nada.
"""
import calendar
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.db import conexion, consultar_uno  # noqa: E402
from app.seguridad import hash_password  # noqa: E402

rnd = random.Random(2026)

CLAVE_DEMO = "Demo2026*"
USUARIOS = [  # usuario, nombre, rol, ip habitual
    ("rrhh", "Laura Mendez (Talento Humano)", "ADMINISTRADOR", "192.168.1.24"),
    ("gerente", "Gerente General", "CONSULTA", "192.168.1.10"),
    ("auditor", "Auditor Interno", "CONSULTA", "192.168.1.31"),
]
IP = {"admin": "192.168.1.5", **{u: ip for u, _, _, ip in USUARIOS}}

APELLIDOS = ["RODRIGUEZ", "MARTINEZ", "GARCIA", "LOPEZ", "HERNANDEZ", "SANCHEZ", "RAMIREZ", "TORRES",
             "DIAZ", "MORENO", "VARGAS", "JIMENEZ", "ROJAS", "MUNOZ", "ORTIZ", "SUAREZ", "PEREZ", "CASTILLO",
             "OSPINA", "MEJIA", "RESTREPO", "VALENCIA", "QUINTERO", "CARDENAS", "PATINO", "SALAZAR", "OSORIO",
             "MONTOYA", "BERMUDEZ", "VELASQUEZ", "NIETO", "PARRA", "CORTES", "GUERRERO", "MOLINA", "ACOSTA"]
NOMBRES_M = ["ANDRES FELIPE", "CARLOS ANDRES", "JUAN SEBASTIAN", "DANIEL", "MIGUEL ANGEL", "SANTIAGO",
             "SERGIO ALEJANDRO", "JORGE IVAN", "NICOLAS", "FELIPE", "ALEJANDRO", "OSCAR JAVIER", "DIEGO ARMANDO"]
NOMBRES_F = ["MARIA CAMILA", "LAURA SOFIA", "VALENTINA", "DANIELA", "ANA MARIA", "PAULA ANDREA", "NATALIA",
             "CAROLINA", "JULIANA", "MARIA FERNANDA", "LINA MARCELA", "DIANA CAROLINA", "SARA", "ANGELA PATRICIA"]

NUEVOS_CATALOGOS = {
    "dependencia": ("nombre_dependencia", ["Talento Humano"]),
    "cargo": ("nombre_cargo", ["Analista de nomina", "Analista de Talento Humano", "Desarrollador Frontend",
                               "Analista contable", "Ejecutivo comercial", "Analista de facturacion"]),
    "eps": ("nombre_eps", ["Compensar EPS", "Salud Total EPS"]),
    "arl": ("nombre_arl", ["ARL Sura", "Colmena Seguros"]),
}
# dependencia -> cargos posibles (con los nombres ya existentes y los nuevos)
CARGOS_POR_DEP = {
    "Tecnología": ["Ingeniero de Desarrollo", "Ingeniero de Soporte", "DBA", "Líder de infraestructura",
                   "Líder de QA", "Desarrollador Frontend"],
    "Facturación": ["Auxiliar especializado", "Director de Facturación", "Analista de facturacion",
                    "Director de cartera"],
    "Contabilidad": ["Director de Impuestos", "Auditor interno", "Director de presupuestos",
                     "Director de costos", "Analista contable"],
    "Comercial": ["Gerente de ventas", "Director de ventas", "Ejecutivo comercial"],
    "Talento Humano": ["Analista de nomina", "Analista de Talento Humano"],
}
N_NUEVOS = 40
MESES = list(range(4, 13))  # abril a diciembre de 2022 (marzo ya viene del archivo del cliente)


# --------------------------------------------------------------------------- reloj simulado
def dias_habiles(desde: date, hasta: date) -> list[date]:
    d, out = desde, []
    while d <= hasta:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


HOY = date.today()
DIAS = dias_habiles(HOY - timedelta(days=24), HOY - timedelta(days=1))


def en(dia: date, h: int, m: int, s: int | None = None) -> datetime:
    return datetime(dia.year, dia.month, dia.day, h, m, rnd.randint(0, 59) if s is None else s)


class Sesion:
    """Una conexion con @app_user y la hora fijada; cada cambio queda auditado con esa hora."""

    def __init__(self, usuario: str):
        self.usuario = usuario
        self._ctx = conexion(usuario)

    def __enter__(self):
        self.con = self._ctx.__enter__()
        self.cur = self.con.cursor()
        return self

    def __exit__(self, *exc):
        self.cur.execute("SET timestamp = DEFAULT")
        self.cur.close()
        return self._ctx.__exit__(*exc)

    def hora(self, t: datetime) -> None:
        self.cur.execute("SET timestamp = UNIX_TIMESTAMP(%s)", (t,))

    def sql(self, q: str, p: tuple = ()) -> int:
        self.cur.execute(q, p)
        return self.cur.lastrowid

    def uno(self, q: str, p: tuple = ()):
        self.cur.execute(q, p)
        return self.cur.fetchone()


EVENTOS: list[tuple] = []


def evento(t: datetime, tipo: str, usuario: str, detalle: str | None = None, ip: str | None = None) -> None:
    EVENTOS.append((tipo, usuario, detalle, ip or IP.get(usuario, "192.168.1.50"), t))


def sesion_web(dia: date, usuario: str, inicio: tuple[int, int], acciones: list[tuple[str, str]],
               fallar_antes: bool = False) -> datetime:
    """Login, accesos/reportes, logout. Devuelve la hora en que termina."""
    t = en(dia, *inicio)
    if fallar_antes:
        evento(t, "LOGIN_FALLIDO", usuario, "Usuario o contrasena incorrectos")
        t += timedelta(seconds=rnd.randint(15, 50))
    evento(t, "LOGIN_OK", usuario)
    for tipo, det in acciones:
        t += timedelta(seconds=rnd.randint(8, 240))
        evento(t, tipo, usuario, det)
    t += timedelta(minutes=rnd.randint(2, 20))
    evento(t, "LOGOUT", usuario)
    return t


def acc(*rutas: str) -> list[tuple[str, str]]:
    return [("ACCESO", f"GET {r} -> 200") for r in rutas]


def rep(nombre: str, pdf: bool, params: dict) -> tuple[str, str]:
    return ("REPORTE", f"{nombre} {'PDF' if pdf else 'pantalla'} {params}")


# --------------------------------------------------------------------------- pasos
def crear_usuarios(dia: date) -> None:
    with Sesion("admin") as s:
        t = en(dia, 8, 12)
        evento(t, "LOGIN_OK", "admin")
        for i, (u, nombre, rol, _) in enumerate(USUARIOS):
            t += timedelta(minutes=2, seconds=rnd.randint(0, 50))
            s.hora(t)
            id_rol = s.uno("SELECT id_rol FROM rol WHERE nombre_rol = %s", (rol,))["id_rol"]
            s.sql("INSERT INTO usuario (nombre_usuario, nombre_completo, password_hash, id_rol) VALUES (%s,%s,%s,%s)",
                  (u, nombre, hash_password(CLAVE_DEMO), id_rol))
            evento(t, "ACCESO", "admin", "POST /api/usuarios -> 201")
        t += timedelta(minutes=4)
        evento(t, "LOGOUT", "admin")


def crear_catalogos(dia: date) -> dict:
    with Sesion("admin") as s:
        t = en(dia, 9, 40)
        evento(t, "LOGIN_OK", "admin")
        rutas = {"dependencia": "dependencias", "cargo": "cargos", "eps": "eps", "arl": "arl"}
        for tabla, (col, valores) in NUEVOS_CATALOGOS.items():
            for v in valores:
                t += timedelta(seconds=rnd.randint(30, 120))
                s.hora(t)
                s.sql(f"INSERT INTO {tabla} ({col}) VALUES (%s)", (v,))
                evento(t, "ACCESO", "admin", f"POST /api/crud/{rutas[tabla]} -> 201")
        evento(t + timedelta(minutes=3), "LOGOUT", "admin")
        ids = {}
        for tabla, pk, col in [("dependencia", "id_dependencia", "nombre_dependencia"),
                               ("cargo", "id_cargo", "nombre_cargo"), ("eps", "id_eps", "nombre_eps"),
                               ("arl", "id_arl", "nombre_arl"), ("fondo_pension", "id_fondo_pension", "nombre_fondo")]:
            s.cur.execute(f"SELECT {pk} AS id, {col} AS n FROM {tabla}")
            ids[tabla] = {f["n"]: f["id"] for f in s.cur.fetchall()}
        return ids


def generar_empleados(ids: dict) -> list[dict]:
    usados, out = set(), []
    deps = list(CARGOS_POR_DEP)
    pesos = [12, 8, 8, 7, 5]
    for i in range(N_NUEVOS):
        while True:
            a1, a2 = rnd.sample(APELLIDOS, 2)
            mujer = rnd.random() < 0.5
            nom = rnd.choice(NOMBRES_F if mujer else NOMBRES_M)
            if (a1, a2, nom) not in usados:
                usados.add((a1, a2, nom))
                break
        dep = rnd.choices(deps, pesos)[0]
        cargo = rnd.choice(CARGOS_POR_DEP[dep])
        base = 4_600_000 if cargo.startswith(("Director", "Gerente", "Líder")) else 3_100_000
        if cargo.startswith(("Auxiliar", "Analista", "Ejecutivo")):
            base = 2_300_000
        ingreso = date(2019, 1, 1) + timedelta(days=rnd.randint(0, 1400))  # 2019 a fines de 2022
        out.append({
            "codigo_empleado": 5021 + i, "primer_apellido": a1, "segundo_apellido": a2, "nombres": nom,
            "fecha_ingreso": ingreso, "salario": round(base * rnd.uniform(0.9, 1.35), -3),
            "id_dependencia": ids["dependencia"][dep], "id_cargo": ids["cargo"][cargo],
            "id_eps": rnd.choice(list(ids["eps"].values())), "id_arl": rnd.choice(list(ids["arl"].values())),
            "id_fondo_pension": rnd.choice(list(ids["fondo_pension"].values())),
        })
    return out


def registrar_empleados(empleados: list[dict], dias: list[date]) -> None:
    """Talento Humano los crea por el CRUD a lo largo de varios dias."""
    lotes = [empleados[i::len(dias)] for i in range(len(dias))]
    for dia, lote in zip(dias, lotes):
        with Sesion("rrhh") as s:
            t = en(dia, 8, rnd.randint(5, 40))
            evento(t, "LOGIN_OK", "rrhh")
            evento(t + timedelta(seconds=20), "ACCESO", "rrhh", "GET /api/crud/empleados -> 200")
            t += timedelta(minutes=1)
            for e in sorted(lote, key=lambda x: x["codigo_empleado"]):
                t += timedelta(minutes=rnd.randint(2, 7), seconds=rnd.randint(0, 59))
                s.hora(t)
                cols = ", ".join(e)
                s.sql(f"INSERT INTO empleado ({cols}) VALUES ({', '.join(['%s'] * len(e))})", tuple(e.values()))
                evento(t, "ACCESO", "rrhh", "POST /api/crud/empleados -> 201")
            evento(t + timedelta(minutes=5), "LOGOUT", "rrhh")


def cargar_nomina(dias: list[date]) -> None:
    """Una carga por mes de abr a dic 2022, como si se subiera el Excel mensual."""
    with Sesion("rrhh") as s0:
        s0.cur.execute("SELECT codigo_empleado, fecha_ingreso FROM empleado")
        empleados = s0.cur.fetchall()
        s0.cur.execute("SELECT id_tipo_novedad, nombre_tipo FROM tipo_novedad")
        tipos = {f["nombre_tipo"]: f["id_tipo_novedad"] for f in s0.cur.fetchall()}
    for mes, dia in zip(MESES, dias):
        with Sesion("rrhh") as s:
            t = en(dia, 14, rnd.randint(0, 40))
            evento(t, "LOGIN_OK", "rrhh")
            s.hora(t + timedelta(seconds=40))
            id_per = s.sql("INSERT INTO periodo (anio, mes) VALUES (2022, %s)", (mes,))
            fin_mes = date(2022, mes, calendar.monthrange(2022, mes)[1])
            insertados = novedades = 0
            for e in empleados:
                if e["fecha_ingreso"] > fin_mes:
                    continue
                dias_nov, nov = 0, None
                r = rnd.random()
                if r < 0.10 or (mes == 12 and r < 0.30):
                    dias_nov = rnd.randint(5, 15)
                    nov = "VACACIONES"
                elif r < 0.17:
                    dias_nov = rnd.randint(1, 8)
                    nov = "INCAPACIDAD"
                trabajados = 30 - dias_nov
                if e["fecha_ingreso"].year == 2022 and e["fecha_ingreso"].month == mes:
                    trabajados = min(trabajados, 30 - e["fecha_ingreso"].day + 1)
                id_nom = s.sql(
                    "INSERT INTO nomina_mensual (codigo_empleado, id_periodo, dias_trabajados, bonificacion, transporte)"
                    " VALUES (%s, %s, %s, %s, %s)",
                    (e["codigo_empleado"], id_per, max(trabajados, 0),
                     round(rnd.uniform(0, 900_000), -3) if rnd.random() < 0.8 else 0,
                     round(rnd.uniform(1_000, 50_000))))
                insertados += 1
                if nov:
                    ini = date(2022, mes, rnd.randint(1, max(1, fin_mes.day - dias_nov)))
                    s.sql("INSERT INTO novedad (id_nomina, id_tipo_novedad, fecha_inicio, fecha_fin, dias)"
                          " VALUES (%s, %s, %s, %s, %s)",
                          (id_nom, tipos[nov], ini, ini + timedelta(days=dias_nov - 1), dias_nov))
                    novedades += 1
            t += timedelta(minutes=1, seconds=rnd.randint(5, 30))
            evento(t, "CARGA_ARCHIVO", "rrhh",
                   f"Nomina_2022-{mes:02d}.xlsx: {insertados + 1 + novedades} insertados, 0 actualizados, 0 rechazados")
            evento(t + timedelta(minutes=2), "REPORTE", "rrhh",
                   f"novedades pantalla {{'desde': '{mes:02d}/2022', 'hasta': '{mes:02d}/2022', 'orden': 'asc'}}")
            evento(t + timedelta(minutes=6), "LOGOUT", "rrhh")


def ajustes(dias: list[date]) -> None:
    """Cambios de un area de RRHH real: aumentos, promociones, traslados, un error corregido."""
    d1, d2, d3, d4 = dias
    with Sesion("rrhh") as s:
        t = en(d1, 10, 5)
        evento(t, "LOGIN_OK", "rrhh")
        for cod, pct in [(5001, 0.08), (5005, 0.06), (5009, 0.12), (5014, 0.10), (5017, 0.07), (5023, 0.05)]:
            t += timedelta(minutes=rnd.randint(1, 4))
            s.hora(t)
            s.sql("UPDATE empleado SET salario = ROUND(salario * %s, -3) WHERE codigo_empleado = %s", (1 + pct, cod))
            evento(t, "ACCESO", "rrhh", f"PUT /api/crud/empleados/{cod} -> 200")
        evento(t + timedelta(minutes=3), "LOGOUT", "rrhh")

        # Promocion: Isabella Camargo pasa de DBA a Lider de infraestructura
        t = en(d2, 11, 20)
        evento(t, "LOGIN_OK", "rrhh")
        s.hora(t + timedelta(minutes=2))
        s.sql("UPDATE empleado SET id_cargo = (SELECT id_cargo FROM cargo WHERE nombre_cargo = 'Líder de infraestructura'),"
              " salario = 3400000 WHERE codigo_empleado = 5009")
        evento(t + timedelta(minutes=2), "ACCESO", "rrhh", "PUT /api/crud/empleados/5009 -> 200")
        # Traslado: Juan Pablo Alarcon pasa a Talento Humano
        s.hora(t + timedelta(minutes=5))
        s.sql("UPDATE empleado SET id_dependencia = (SELECT id_dependencia FROM dependencia WHERE nombre_dependencia = 'Talento Humano'),"
              " id_cargo = (SELECT id_cargo FROM cargo WHERE nombre_cargo = 'Analista de Talento Humano')"
              " WHERE codigo_empleado = 5002")
        evento(t + timedelta(minutes=5), "ACCESO", "rrhh", "PUT /api/crud/empleados/5002 -> 200")
        # Cambio de EPS solicitado por un empleado
        s.hora(t + timedelta(minutes=9))
        s.sql("UPDATE empleado SET id_eps = (SELECT id_eps FROM eps WHERE nombre_eps = 'Compensar EPS') WHERE codigo_empleado = 5012")
        evento(t + timedelta(minutes=9), "ACCESO", "rrhh", "PUT /api/crud/empleados/5012 -> 200")
        evento(t + timedelta(minutes=14), "LOGOUT", "rrhh")

        # Error de digitacion: empleado creado dos veces y luego borrado
        t = en(d3, 15, 2)
        evento(t, "LOGIN_OK", "rrhh")
        s.hora(t + timedelta(minutes=1))
        s.sql("INSERT INTO empleado (codigo_empleado, primer_apellido, segundo_apellido, nombres, fecha_ingreso, salario,"
              " id_dependencia, id_cargo, id_eps, id_arl, id_fondo_pension)"
              " SELECT 5099, primer_apellido, segundo_apellido, nombres, fecha_ingreso, salario, id_dependencia, id_cargo,"
              " id_eps, id_arl, id_fondo_pension FROM empleado WHERE codigo_empleado = 5030")
        evento(t + timedelta(minutes=1), "ACCESO", "rrhh", "POST /api/crud/empleados -> 201")
        s.hora(t + timedelta(minutes=6))
        s.sql("DELETE FROM empleado WHERE codigo_empleado = 5099")
        evento(t + timedelta(minutes=6), "ACCESO", "rrhh", "DELETE /api/crud/empleados/5099 -> 200")
        # Incapacidad que se extendio: se corrige la novedad de marzo
        s.hora(t + timedelta(minutes=11))
        s.sql("UPDATE novedad SET fecha_fin = '2022-03-23', dias = 22 WHERE id_novedad = 1")
        evento(t + timedelta(minutes=11), "ACCESO", "rrhh", "PUT /api/crud/novedades/1 -> 200")
        evento(t + timedelta(minutes=15), "LOGOUT", "rrhh")

    # El administrador ajusta un parametro de nomina
    with Sesion("admin") as s:
        t = en(d4, 16, 30)
        evento(t, "LOGIN_OK", "admin")
        s.hora(t + timedelta(minutes=6))
        s.sql("UPDATE parametro_nomina SET descripcion = 'Porcentaje de aporte a pension a cargo del empleado'"
              " WHERE clave = 'PORC_APORTE_PENSION_EMPLEADO'")
        evento(t + timedelta(minutes=6), "ACCESO", "admin", "PUT /api/crud/parametros/1 -> 200")
        evento(t + timedelta(minutes=10), "LOGOUT", "admin")


def actividad_diaria() -> None:
    """Uso normal del sistema: consultas de gerencia, revisiones de auditoria e intentos fallidos."""
    rango = {"desde": "01/2022", "hasta": "12/2022", "orden": "asc"}
    for i, dia in enumerate(DIAS):
        # Gerencia revisa reportes casi todos los dias
        if rnd.random() < 0.85:
            acciones = acc("/api/auth/yo")
            for _ in range(rnd.randint(1, 4)):
                r = rnd.choice([
                    rep("nomina", rnd.random() < 0.3, {"orden": rnd.choice(["asc", "desc"])}),
                    rep("salud-pension", rnd.random() < 0.3, {"orden": "asc"}),
                    rep("novedades", rnd.random() < 0.4, rango),
                    rep("personal", False, {"codigo": str(rnd.randint(5001, 5060))}),
                    rep("entretenimiento", rnd.random() < 0.3,
                        {"anio_desde": "1990", "anio_hasta": "2005", "n_top": "10", "n_generos": "3", "orden": "desc"}),
                ])
                acciones.append(r)
            sesion_web(dia, "gerente", (rnd.randint(8, 16), rnd.randint(0, 59)), acciones,
                       fallar_antes=rnd.random() < 0.12)
        # El auditor revisa la bitacora dos veces por semana
        if dia.weekday() in (1, 3):
            desde = (dia - timedelta(days=7)).strftime("%Y-%m-%d")
            sesion_web(dia, "auditor", (rnd.randint(9, 11), rnd.randint(0, 59)), [
                *acc("/api/auth/yo"),
                ("REPORTE", f"auditoria pantalla {{'desde': '{desde}', 'hasta': '{dia}', 'usuario': ''}}"),
                ("REPORTE", f"auditoria PDF {{'desde': '{desde}', 'hasta': '{dia}', 'usuario': ''}}"),
            ])
        # Talento Humano consulta empleados
        if rnd.random() < 0.6:
            sesion_web(dia, "rrhh", (rnd.randint(13, 17), rnd.randint(0, 59)), [
                *acc("/api/auth/yo", "/api/crud", "/api/crud/empleados",
                     f"/api/crud/empleados?pagina={rnd.randint(1, 3)}", "/api/crud/nominas"),
                rep("personal", rnd.random() < 0.5, {"codigo": str(rnd.randint(5001, 5060))}),
            ])
        # Intentos sospechosos desde fuera de la red (los detecta el reporte de auditoria)
        if i % 6 == 2:
            t = en(dia, rnd.choice([2, 3, 23]), rnd.randint(0, 59))
            ip = f"181.{rnd.randint(48, 63)}.{rnd.randint(0, 255)}.{rnd.randint(1, 254)}"
            for u in rnd.sample(["root", "administrador", "admin", "test", "sa", "usuario"], 4):
                t += timedelta(seconds=rnd.randint(2, 9))
                evento(t, "LOGIN_FALLIDO", u, "Usuario o contrasena incorrectos", ip)
            evento(t + timedelta(seconds=5), "LOGIN_FALLIDO", "admin", "Captcha incorrecto", ip)


def guardar_eventos() -> None:
    EVENTOS.sort(key=lambda e: e[4])
    with conexion("SISTEMA") as con, con.cursor() as cur:
        cur.executemany(
            "INSERT INTO auditoria_evento (tipo, usuario_app, detalle, ip, fecha) VALUES (%s, %s, %s, %s, %s)",
            [(tp, u, (d or "")[:500] or None, ip, f) for tp, u, d, ip, f in EVENTOS])


def main() -> None:
    if consultar_uno("SELECT 1 AS x FROM empleado WHERE codigo_empleado = 5021"):
        sys.exit("Los datos de demostracion ya estan cargados (existe el empleado 5021).")
    if not consultar_uno("SELECT 1 AS x FROM empleado WHERE codigo_empleado = 5001"):
        sys.exit("Primero cargue los archivos del cliente: uv run python scripts/cargar_datos.py")
    if len(DIAS) < 15:
        sys.exit("No hay suficientes dias habiles en el rango")

    crear_usuarios(DIAS[0])
    ids = crear_catalogos(DIAS[0])
    registrar_empleados(generar_empleados(ids), DIAS[1:4])
    cargar_nomina(DIAS[4:13])
    ajustes([DIAS[6], DIAS[9], DIAS[12], DIAS[14]])
    actividad_diaria()
    guardar_eventos()

    r = consultar_uno("SELECT (SELECT COUNT(*) FROM empleado) AS e, (SELECT COUNT(*) FROM nomina_mensual) AS n,"
                      " (SELECT COUNT(*) FROM novedad) AS v, (SELECT COUNT(*) FROM usuario) AS u")
    print(f"Empleados: {r['e']}  Liquidaciones: {r['n']}  Novedades: {r['v']}  Usuarios: {r['u']}")
    print(f"Eventos de auditoria agregados: {len(EVENTOS)}  ({DIAS[0]} a {DIAS[-1]})")
    print(f"Usuarios demo: {', '.join(u for u, *_ in USUARIOS)}  (contrasena: {CLAVE_DEMO})")


if __name__ == "__main__":
    main()
