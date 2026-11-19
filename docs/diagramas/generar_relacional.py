"""Genera los diagramas del modelo relacional (pata de gallo) leyendo los scripts SQL."""
import re, subprocess, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]
sql = (RAIZ/"db/01_esquema.sql").read_text() + (RAIZ/"db/02_seguridad.sql").read_text()
tablas = {}
for m in re.finditer(r"CREATE TABLE (\w+) \((.*?)\) ENGINE", sql, re.S):
    nombre, cuerpo = m.group(1), m.group(2)
    cols, pk, fks, uq = [], [], {}, set()
    for ln in cuerpo.splitlines():
        ln = ln.strip().rstrip(",")
        if not ln or ln.startswith("--"): continue
        if ln.startswith("CONSTRAINT"):
            if "PRIMARY KEY" in ln: pk = [c.strip() for c in re.search(r"\((.*?)\)", ln).group(1).split(",")]
            elif "UNIQUE" in ln: uq |= {c.strip() for c in re.search(r"\((.*?)\)", ln).group(1).split(",")}
            elif "FOREIGN KEY" in ln:
                fk = re.search(r"FOREIGN KEY \((\w+)\)", ln).group(1); fks[fk] = None
            continue
        if ln.startswith("REFERENCES"):
            t = re.search(r"REFERENCES (\w+)", ln).group(1); last = list(fks)[-1]; fks[last] = t; continue
        p = ln.split()
        tipo = re.sub(r"\s+", "", " ".join(p[1:]).split(" NOT")[0].split(" NULL")[0].split(" DEFAULT")[0])
        cols.append((p[0], p[1]))
    tablas[nombre] = dict(cols=cols, pk=pk, fks=fks, uq=uq)

MODULOS = {
 "rel_nomina": (["dependencia","cargo","eps","arl","fondo_pension","empleado","periodo","nomina_mensual","tipo_novedad","novedad","parametro_nomina"], "#dbeafe"),
 "rel_entretenimiento": (["pelicula","genero","pelicula_genero","editorial","idioma","libro","autor","libro_autor","serie","libro_serie"], "#dcfce7"),
 "rel_seguridad": (["rol","usuario","auditoria_datos","auditoria_evento"], "#fee2e2"),
}
for archivo, (lista, color) in MODULOS.items():
    out = ['digraph G { rankdir=LR; dpi=200; nodesep=0.35; ranksep=1.1; splines=spline;',
           'node [shape=plaintext, fontname="Helvetica"]; edge [arrowhead=crowodot, arrowtail=teetee, dir=both, color="#334155", penwidth=1.2];']
    for t in lista:
        d = tablas[t]
        filas = [f'<tr><td bgcolor="{color}" colspan="3"><b>{t}</b></td></tr>']
        for c, tipo in d["cols"]:
            marca = ("PK" if c in d["pk"] else "") + (" FK" if c in d["fks"] else "") + (" UQ" if c in d["uq"] and c not in d["pk"] else "")
            nom = f"<u>{c}</u>" if c in d["pk"] else c
            filas.append(f'<tr><td align="left" port="{c}"><font point-size="9">{marca.strip() or " "}</font></td><td align="left">{nom}</td><td align="left"><font color="#64748b" point-size="9">{tipo.lower()}</font></td></tr>')
        out.append(f'{t} [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="3">{"".join(filas)}</table>>];')
    for t in lista:
        for fk, ref in tablas[t]["fks"].items():
            if ref in lista:
                out.append(f'{ref} -> {t}:{fk};')
    out.append("}")
    dotf = Path(__file__).with_name(archivo + ".dot"); dotf.write_text("\n".join(out))
    subprocess.run(["dot", "-Tpng", str(dotf), "-o", str(RAIZ/"docs/img"/(archivo+".png"))], check=True)
    print(archivo, "ok")
