"""Arma los documentos finales (informe y manual) y los convierte a DOCX y PDF en formato APA 7.

- {{ARCHIVO:ruta}}       -> bloque de código con el contenido del archivo (ruta relativa a la raíz)
- {{ARCHIVO:ruta:a-b}}   -> solo las líneas a..b
- {{DICCIONARIO}}        -> diccionario de datos generado desde db/01_esquema.sql y db/02_seguridad.sql

Uso:  python docs/construir.py [informe-ingenieria] [manual-usuario]   (requiere python-docx y LibreOffice)
"""
import re
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
RAIZ = DOCS.parent
GENERADOR = DOCS / "apa_docx.py"  # copia de la skill apa7 con bloques de código, anchos de tabla y listas numeradas


def tablas_sql() -> dict:
    sql = (RAIZ / "db/01_esquema.sql").read_text() + (RAIZ / "db/02_seguridad.sql").read_text()
    tablas = {}
    for m in re.finditer(r"CREATE TABLE (\w+) \((.*?)\) ENGINE", sql, re.S):
        cols, pk, fks, uq, checks = [], [], {}, [], []
        ultima_fk = None
        for ln in m.group(2).splitlines():
            ln = ln.strip().rstrip(",")
            if not ln or ln.startswith("--"):
                continue
            if ln.startswith("CONSTRAINT"):
                lista = re.search(r"\((.*?)\)", ln)
                if "PRIMARY KEY" in ln:
                    pk = [c.strip() for c in lista.group(1).split(",")]
                elif "UNIQUE" in ln:
                    uq.append([c.strip() for c in lista.group(1).split(",")])
                elif "FOREIGN KEY" in ln:
                    ultima_fk = re.search(r"FOREIGN KEY \((\w+)\)", ln).group(1)
                elif "CHECK" in ln:
                    checks.append(ln.split("CHECK", 1)[1].strip())
                continue
            if ln.startswith("REFERENCES"):
                fks[ultima_fk] = re.search(r"REFERENCES (\w+) \((\w+)\)", ln).groups()
                continue
            if ln.startswith(("ON ", "FOR ")):
                continue
            partes = ln.split()
            nombre, tipo = partes[0], partes[1]
            resto = " ".join(partes[2:]).split("--")[0]
            nulo = "No" if "NOT NULL" in resto else "Sí"
            defecto = re.search(r"DEFAULT (\S+)", resto)
            cols.append((nombre, tipo.lower(), nulo, defecto.group(1) if defecto else ""))
        tablas[m.group(1)] = dict(cols=cols, pk=pk, fks=fks, uq=uq, checks=checks)
    return tablas


def diccionario(n_inicial: int) -> str:
    salida, n = [], n_inicial
    for nombre, t in tablas_sql().items():
        salida.append(f"La Tabla {n} describe la tabla *{nombre}*.")
        salida.append("")
        salida.append(f"Tabla: Diccionario de Datos de la Tabla {nombre}")
        salida.append("| Columna | Tipo | Nulo | Restricción |")
        salida.append("|---|---|---|---|")
        for c, tipo, nulo, defecto in t["cols"]:
            r = []
            if c in t["pk"]:
                r.append("PK")
            if c in t["fks"]:
                r.append(f"FK a {t['fks'][c][0]}")
            for u in t["uq"]:
                if c in u and c not in t["pk"]:
                    r.append("UNIQUE" + (f" ({', '.join(u)})" if len(u) > 1 else ""))
            if defecto:
                r.append(f"DEFAULT {defecto}")
            salida.append(f"| {c} | {tipo} | {nulo} | {'; '.join(r) or '—'} |")
        nota = "Restricciones CHECK: " + "; ".join(t["checks"]) + "." if t["checks"] else "Sin restricciones CHECK."
        salida.append(f"Nota: {nota.replace('|', '/')}")
        salida.append("")
        n += 1
    return "\n".join(salida)


def incluir(m: re.Match) -> str:
    ruta, rango = m.group(1), m.group(2)
    lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()
    if rango:
        a, b = (int(x) for x in rango.split("-"))
        lineas = lineas[a - 1 : b]
    return "```\n" + "\n".join(lineas) + "\n```"


def construir(nombre: str) -> None:
    fuente = (DOCS / f"{nombre}.fuente.md").read_text(encoding="utf-8")
    if "{{DICCIONARIO}}" in fuente:
        previo = fuente.split("{{DICCIONARIO}}")[0]
        n = len(re.findall(r"^Tabla:", previo, re.M)) + 1
        fuente = fuente.replace("{{DICCIONARIO}}", diccionario(n))
    fuente = re.sub(r"\{\{ARCHIVO:([^:}]+)(?::(\d+-\d+))?\}\}", incluir, fuente)
    salida = DOCS / f"{nombre}.md"
    salida.write_text(fuente, encoding="utf-8")
    subprocess.run([sys.executable, str(GENERADOR), str(salida), "--pdf"], check=True)


if __name__ == "__main__":
    for doc in (sys.argv[1:] or ["informe-ingenieria", "manual-usuario"]):
        if (DOCS / f"{doc}.fuente.md").exists():
            construir(doc)
