"""Carga de libros desde el archivo JSON (RF-07).

Cada objeto trae 12 campos (+ FIELD13). Transformaciones:
- Si FIELD13 no esta vacio, el nombre del autor tenia una coma y los campos llegaron desplazados
  una posicion: se unen authors + average_rating y se corre todo a la izquierda.
- Autores separados por '/', con su orden.
- Fecha de mes/dia/ano a DATE.
- Serie extraida del titulo: "Titulo (Serie  #3)".
- ISBN repetido: se rechaza el segundo libro (restriccion UNIQUE).
"""
import json
import re
from datetime import date

import pymysql

from .comun import ErrorEstructura, Resumen, id_catalogo

CAMPOS = ["bookID", "title", "authors", "average_rating", "isbn", "isbn13", "language_code",
          "num_pages", "ratings_count", "text_reviews_count", "publication_date", "publisher"]
_DESPLAZABLES = CAMPOS[3:] + ["FIELD13"]
_RE_SERIE = re.compile(r"\((?P<serie>[^()]+?),?\s*#\s*(?P<num>[^()]+?)\)\s*$")


def _realinear(o: dict) -> dict:
    o = dict(o)
    o["authors"] = f"{o['authors']},{o['average_rating']}"
    for actual, siguiente in zip(_DESPLAZABLES, _DESPLAZABLES[1:]):
        o[actual] = o[siguiente]
    o["FIELD13"] = ""
    return o


def _fecha(txt: str) -> date | None:
    m, d, a = (int(x) for x in str(txt).strip().split("/"))
    return date(a, m, d)


def _isbn(v) -> str | None:
    s = str(v).strip().upper() if v is not None else ""
    return s or None


def parsear(contenido: bytes) -> tuple[list[dict], Resumen]:
    r = Resumen("libros")
    try:
        datos = json.loads(contenido.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErrorEstructura(f"El archivo no es un JSON valido: {exc}")
    if not isinstance(datos, list) or not datos or not isinstance(datos[0], dict):
        raise ErrorEstructura("Se esperaba una lista de objetos de libros")
    faltan = [c for c in CAMPOS if c not in datos[0]]
    if faltan:
        raise ErrorEstructura(f"La estructura no corresponde, faltan campos: {', '.join(faltan)}")

    registros, ids, isbns, isbns13 = [], set(), set(), set()
    for o in datos:
        r.leidos += 1
        ref = o.get("bookID", f"posicion {r.leidos}")
        if str(o.get("FIELD13") or "").strip():
            o = _realinear(o)
            r.avisos.append(f"Libro {ref}: campos desplazados por una coma en el autor, realineados")
        try:
            lid = int(o["bookID"])
            titulo = str(o["title"]).strip()
            if not titulo:
                raise ValueError("titulo vacio")
            rating = float(o["average_rating"])
            if not 0 <= rating <= 5:
                raise ValueError(f"calificacion fuera de rango: {rating}")
            paginas = int(o["num_pages"])
            n_ratings = int(o["ratings_count"])
            n_resenas = int(o["text_reviews_count"])
            if min(paginas, n_ratings, n_resenas) < 0:
                raise ValueError("valores negativos")
        except (KeyError, TypeError, ValueError) as exc:
            r.rechazar(ref, f"Tipo de dato invalido: {exc}")
            continue
        try:
            fecha = _fecha(o["publication_date"])
        except (ValueError, TypeError):
            fecha = None
            r.avisos.append(f"Libro {lid}: fecha invalida {o['publication_date']!r}, se carga sin fecha")

        isbn, isbn13 = _isbn(o["isbn"]), _isbn(o["isbn13"])
        if isbn and len(isbn) > 10 or isbn13 and len(isbn13) != 13:
            r.rechazar(lid, f"ISBN con longitud invalida: {isbn} / {isbn13}")
            continue
        if lid in ids:
            r.rechazar(lid, "Identificador repetido en el archivo")
            continue
        if (isbn and isbn in isbns) or (isbn13 and isbn13 in isbns13):
            r.rechazar(lid, f"ISBN repetido en el archivo: {isbn} / {isbn13}")
            continue
        ids.add(lid)
        isbns.add(isbn)
        isbns13.add(isbn13)

        autores = list(dict.fromkeys(a.strip() for a in str(o["authors"]).split("/") if a.strip()))
        m = _RE_SERIE.search(titulo)
        registros.append({
            "id": lid, "titulo": titulo[:255], "isbn": isbn, "isbn13": isbn13,
            "paginas": paginas, "fecha": fecha, "rating": round(rating, 2),
            "n_ratings": n_ratings, "n_resenas": n_resenas,
            "editorial": (str(o["publisher"]).strip() or "SIN EDITORIAL")[:150],
            "idioma": (str(o["language_code"]).strip() or "und")[:10],
            "autores": [a[:150] for a in autores] or ["SIN AUTOR"],
            "serie": m["serie"].strip()[:150] if m else None,
            "num_serie": m["num"].strip()[:20] if m else None,
        })
    return registros, r


def cargar(cur, registros: list[dict], r: Resumen) -> None:
    cache_ed, cache_id, cache_au, cache_se = {}, {}, {}, {}
    for b in registros:
        cur.execute("SAVEPOINT libro")
        try:
            id_ed = id_catalogo(cur, cache_ed, "editorial", "id_editorial", "nombre_editorial", b["editorial"])
            id_idi = id_catalogo(cur, cache_id, "idioma", "id_idioma", "codigo_idioma", b["idioma"])
            n = cur.execute(
                """INSERT INTO libro (id_libro, titulo, isbn, isbn13, num_paginas, fecha_publicacion,
                                      rating_promedio, cantidad_ratings, cantidad_resenas, id_editorial, id_idioma)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), isbn = VALUES(isbn), isbn13 = VALUES(isbn13),
                     num_paginas = VALUES(num_paginas), fecha_publicacion = VALUES(fecha_publicacion),
                     rating_promedio = VALUES(rating_promedio), cantidad_ratings = VALUES(cantidad_ratings),
                     cantidad_resenas = VALUES(cantidad_resenas), id_editorial = VALUES(id_editorial),
                     id_idioma = VALUES(id_idioma)""",
                (b["id"], b["titulo"], b["isbn"], b["isbn13"], b["paginas"], b["fecha"], b["rating"],
                 b["n_ratings"], b["n_resenas"], id_ed, id_idi),
            )
            autores = [(b["id"], id_catalogo(cur, cache_au, "autor", "id_autor", "nombre_autor", a), i)
                       for i, a in enumerate(b["autores"], start=1)]
            # Un mismo autor puede venir con distinto nombre que colapsa por la colacion: se deja el primero
            vistos, unicos = set(), []
            for t in autores:
                if t[1] not in vistos:
                    vistos.add(t[1])
                    unicos.append(t)
            # Las relaciones solo se reescriben si cambiaron (evita ruido en la auditoria al recargar)
            cur.execute("SELECT id_libro, id_autor, orden FROM libro_autor WHERE id_libro = %s", (b["id"],))
            if {(f["id_libro"], f["id_autor"], f["orden"]) for f in cur.fetchall()} != set(unicos):
                cur.execute("DELETE FROM libro_autor WHERE id_libro = %s", (b["id"],))
                cur.executemany("INSERT INTO libro_autor (id_libro, id_autor, orden) VALUES (%s, %s, %s)", unicos)
            nueva = set()
            if b["serie"]:
                id_se = id_catalogo(cur, cache_se, "serie", "id_serie", "nombre_serie", b["serie"])
                nueva = {(b["id"], id_se, b["num_serie"])}
            cur.execute("SELECT id_libro, id_serie, numero_en_serie FROM libro_serie WHERE id_libro = %s", (b["id"],))
            if {(f["id_libro"], f["id_serie"], f["numero_en_serie"]) for f in cur.fetchall()} != nueva:
                cur.execute("DELETE FROM libro_serie WHERE id_libro = %s", (b["id"],))
                cur.executemany("INSERT INTO libro_serie (id_libro, id_serie, numero_en_serie) VALUES (%s, %s, %s)",
                                list(nueva))
            cur.execute("RELEASE SAVEPOINT libro")
            r.contar(n)
        except pymysql.IntegrityError as exc:
            cur.execute("ROLLBACK TO SAVEPOINT libro")
            # Los catalogos creados dentro del savepoint se deshicieron: se limpia la cache
            for c in (cache_ed, cache_id, cache_au, cache_se):
                c.clear()
            r.rechazar(b["id"], f"Viola una restriccion de la base de datos: {exc.args[1] if len(exc.args) > 1 else exc}")
