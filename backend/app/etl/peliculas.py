"""Carga de peliculas desde el archivo DAT (RF-06).

Formato por linea:  id::Titulo (Ano)::Genero1|Genero2|...
Transformacion: se extrae el ano del final del titulo y se dividen los generos por '|'.
'(no genres listed)' se carga como pelicula sin generos.
"""
import re

from .comun import ErrorEstructura, Resumen, id_catalogo

SIN_GENEROS = "(no genres listed)"
_RE_TITULO = re.compile(r"^(?P<titulo>.+?)\s*\((?P<anio>\d{4})\)\s*$")


def parsear(contenido: bytes) -> tuple[list[dict], Resumen]:
    """Valida y limpia el archivo. No toca la base de datos."""
    r = Resumen("peliculas")
    texto = contenido.decode("utf-8", errors="replace")
    lineas = [ln for ln in texto.splitlines() if ln.strip()]
    if not lineas:
        raise ErrorEstructura("El archivo de peliculas esta vacio")
    if lineas[0].count("::") != 2:
        raise ErrorEstructura("La estructura no corresponde: se esperaban 3 campos separados por '::'")

    registros, vistos = [], set()
    for n, ln in enumerate(lineas, start=1):
        r.leidos += 1
        partes = ln.split("::")
        if len(partes) != 3:
            r.rechazar(n, f"Se esperaban 3 campos y llegaron {len(partes)}")
            continue
        sid, titulo_anio, generos = (p.strip() for p in partes)
        if not sid.isdigit():
            r.rechazar(n, f"Identificador no numerico: {sid!r}")
            continue
        m = _RE_TITULO.match(titulo_anio)
        if not m:
            r.rechazar(n, f"No se encontro el ano al final del titulo: {titulo_anio!r}")
            continue
        anio = int(m["anio"])
        if not 1880 <= anio <= 2100:
            r.rechazar(n, f"Ano fuera de rango: {anio}")
            continue
        pid = int(sid)
        if pid in vistos:
            r.rechazar(n, f"Identificador repetido en el archivo: {pid}")
            continue
        vistos.add(pid)
        lista = [] if generos == SIN_GENEROS or not generos else sorted({g.strip() for g in generos.split("|") if g.strip()})
        registros.append({"id": pid, "titulo": m["titulo"][:255], "anio": anio, "generos": lista})
    return registros, r


def cargar(cur, registros: list[dict], r: Resumen) -> None:
    """Inserta o actualiza dentro de la transaccion abierta por el llamador (RF-09)."""
    cache_generos: dict[str, int] = {}
    for p in registros:
        n = cur.execute(
            """INSERT INTO pelicula (id_pelicula, titulo, anio) VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), anio = VALUES(anio)""",
            (p["id"], p["titulo"], p["anio"]),
        )
        r.contar(n)
        ids = [id_catalogo(cur, cache_generos, "genero", "id_genero", "nombre_genero", g) for g in p["generos"]]
        # Sincroniza la relacion: borra los generos que ya no estan y agrega los nuevos
        if ids:
            marcas = ", ".join(["%s"] * len(ids))
            cur.execute(f"DELETE FROM pelicula_genero WHERE id_pelicula = %s AND id_genero NOT IN ({marcas})",
                        (p["id"], *ids))
            cur.executemany("INSERT IGNORE INTO pelicula_genero (id_pelicula, id_genero) VALUES (%s, %s)",
                            [(p["id"], g) for g in ids])
        else:
            cur.execute("DELETE FROM pelicula_genero WHERE id_pelicula = %s", (p["id"],))
