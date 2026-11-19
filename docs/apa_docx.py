#!/usr/bin/env python3
"""Convierte un markdown con metadatos en un .docx con formato APA 7 (guía UMB).

Uso:
    apa_docx.py entrada.md [-o salida.docx] [--pdf]

Formato de entrada: ver ../assets/plantilla.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

SKILL_DIR = Path.home() / ".claude/skills/apa7"
LOGO_UMB = SKILL_DIR / "assets" / "logo-umb.png"

FUENTES = {
    "times": ("Times New Roman", 12),
    "arial": ("Arial", 11),
    "calibri": ("Calibri", 11),
    "georgia": ("Georgia", 11),
    "lucida": ("Lucida Sans Unicode", 10),
}

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

SANGRIA = Inches(0.5)
ANCHO_TEXTO = Inches(6.5)  # carta (8.5") menos 1" de margen a cada lado
ANCHO_MAX_FIGURA = Inches(6.0)

avisos: list[str] = []


# --------------------------------------------------------------------------- utilidades XML


def poner_fuente(rpr_padre, nombre: str) -> None:
    """Fija la fuente en un <w:rPr> y quita las fuentes del tema, que la sobrescribirían."""
    rpr = rpr_padre.get_or_add_rPr()
    fuentes = rpr.find(qn("w:rFonts"))
    if fuentes is None:
        fuentes = OxmlElement("w:rFonts")
        rpr.insert(0, fuentes)
    for atributo in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fuentes.attrib.pop(qn(atributo), None)
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fuentes.set(qn(atributo), nombre)


def poner_idioma(estilo, idioma: str = "es-CO") -> None:
    rpr = estilo.element.get_or_add_rPr()
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), idioma)
    lang.set(qn("w:eastAsia"), idioma)


def campo_pagina(parrafo) -> None:
    """Inserta el campo PAGE (número de página automático)."""
    run = parrafo.add_run()
    for tipo, texto in (("begin", None), (None, " PAGE "), ("separate", None), (None, "1"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        elif texto == "1":
            el = OxmlElement("w:t")
            el.text = texto
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = texto
        run._r.append(el)


def bordes_tabla(tabla) -> None:
    """Solo línea superior e inferior; sin verticales (estilo APA)."""
    tblpr = tabla._tbl.tblPr
    bordes = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{lado}")
        if lado in ("top", "bottom"):
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "8")
            el.set(qn("w:color"), "000000")
        else:
            el.set(qn("w:val"), "nil")
        bordes.append(el)
    existente = tblpr.find(qn("w:tblBorders"))
    if existente is not None:
        tblpr.remove(existente)
    tblpr.append(bordes)


def borde_inferior_celda(celda) -> None:
    tcpr = celda._tc.get_or_add_tcPr()
    bordes = OxmlElement("w:tcBorders")
    abajo = OxmlElement("w:bottom")
    abajo.set(qn("w:val"), "single")
    abajo.set(qn("w:sz"), "8")
    abajo.set(qn("w:color"), "000000")
    bordes.append(abajo)
    tcpr.append(bordes)


def repetir_cabecera(fila) -> None:
    trpr = fila._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)


# --------------------------------------------------------------------------- texto en línea

PATRON_INLINE = re.compile(r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*)")


def agregar_texto(parrafo, texto: str, negrita=False, cursiva=False, tamano=None) -> None:
    """Agrega texto con ***negrita cursiva***, **negrita** y *cursiva* de markdown."""
    for trozo in PATRON_INLINE.split(texto):
        if not trozo:
            continue
        b, i, t = negrita, cursiva, trozo
        if trozo.startswith("***") and trozo.endswith("***") and len(trozo) > 6:
            b, i, t = True, True, trozo[3:-3]
        elif trozo.startswith("**") and trozo.endswith("**") and len(trozo) > 4:
            b, t = True, trozo[2:-2]
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            i, t = True, trozo[1:-1]
        run = parrafo.add_run(t)
        run.bold = b or None
        run.italic = i or None
        if tamano:
            run.font.size = Pt(tamano)


def texto_plano(texto: str) -> str:
    return PATRON_INLINE.sub(lambda m: m.group(0).strip("*"), texto)


def clave_orden(texto: str) -> str:
    plano = unicodedata.normalize("NFKD", texto_plano(texto))
    return "".join(c for c in plano if not unicodedata.combining(c)).casefold()


# --------------------------------------------------------------------------- lectura del markdown


@dataclass
class Bloque:
    tipo: str  # titulo, parrafo, cita, lista, tabla, figura, nota, salto
    texto: str = ""
    nivel: int = 0
    filas: list[list[str]] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    ordenada: bool = False
    ruta: str = ""


def leer_metadatos(texto: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    if not texto.startswith("---"):
        return meta, texto
    fin = texto.find("\n---", 3)
    if fin == -1:
        return meta, texto
    for linea in texto[3:fin].splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or ":" not in linea:
            continue
        clave, valor = linea.split(":", 1)
        meta[clave.strip().lower()] = valor.strip().strip('"').strip("'")
    return meta, texto[fin + 4 :].lstrip("\n")


def leer_bloques(cuerpo: str) -> list[Bloque]:
    lineas = cuerpo.splitlines()
    bloques: list[Bloque] = []
    i = 0
    while i < len(lineas):
        linea = lineas[i].rstrip()
        s = linea.strip()

        if not s or s.startswith("<!--"):
            i += 1
            continue

        if s.startswith("```"):
            codigo = []
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                codigo.append(lineas[i].rstrip())
                i += 1
            i += 1
            bloques.append(Bloque("codigo", items=codigo))
            continue

        if s in ("\\newpage", "\\pagebreak"):
            bloques.append(Bloque("salto"))
            i += 1
            continue

        m = re.match(r"^(#{1,5})\s+(.*)$", s)
        if m:
            bloques.append(Bloque("titulo", m.group(2).strip(), nivel=len(m.group(1))))
            i += 1
            continue

        m = re.match(r"^Tabla:\s*(.+)$", s)
        if m:
            titulo, filas = m.group(1).strip(), []
            i += 1
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            bloques.append(Bloque("tabla", titulo, filas=filas))
            continue

        m = re.match(r"^!\[(.*?)\]\((.+?)\)$", s)
        if m:
            bloques.append(Bloque("figura", m.group(1).strip(), ruta=m.group(2).strip()))
            i += 1
            continue

        m = re.match(r"^Nota:\s*(.+)$", s)
        if m and bloques and bloques[-1].tipo in ("tabla", "figura"):
            bloques.append(Bloque("nota", m.group(1).strip()))
            i += 1
            continue

        if s.startswith(">"):
            parrafos, actual = [], []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                contenido = lineas[i].strip()[1:].strip()
                if contenido:
                    actual.append(contenido)
                elif actual:
                    parrafos.append(" ".join(actual))
                    actual = []
                i += 1
            if actual:
                parrafos.append(" ".join(actual))
            bloques.append(Bloque("cita", items=parrafos))
            continue

        m = re.match(r"^([-*+]|\d+[.)])\s+(.*)$", s)
        if m:
            ordenada = m.group(1)[0].isdigit()
            items = []
            while i < len(lineas):
                mm = re.match(r"^\s*([-*+]|\d+[.)])\s+(.*)$", lineas[i])
                if mm:
                    items.append(mm.group(2).strip())
                elif lineas[i].strip() and items and lineas[i].startswith((" ", "\t")):
                    items[-1] += " " + lineas[i].strip()
                else:
                    break
                i += 1
            bloques.append(Bloque("lista", items=items, ordenada=ordenada))
            continue

        # Párrafo: líneas seguidas hasta una línea vacía o un bloque especial.
        partes = [s]
        i += 1
        while i < len(lineas):
            sig = lineas[i].strip()
            if not sig or re.match(r"^(```|#{1,5}\s|>|Tabla:|!\[|[-*+]\s|\d+[.)]\s|\\newpage|\\pagebreak)", sig):
                break
            partes.append(sig)
            i += 1
        bloques.append(Bloque("parrafo", " ".join(partes)))
    return bloques


# --------------------------------------------------------------------------- documento


class DocumentoAPA:
    def __init__(self, meta: dict[str, str], base: Path):
        self.meta = meta
        self.base = base
        clave_fuente = meta.get("fuente", "times").lower().split()[0]
        if clave_fuente not in FUENTES:
            avisos.append(f"Fuente '{clave_fuente}' desconocida; se usa Times New Roman 12.")
            clave_fuente = "times"
        self.fuente, self.tamano = FUENTES[clave_fuente]
        self.tamano_nota = 10 if clave_fuente == "times" else max(self.tamano - 1, 9)
        self.doc = Document()
        self.n_tablas = 0
        self.n_figuras = 0
        self._preparar()

    # ----- estilos y página

    def _preparar(self) -> None:
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for lado in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
            setattr(sec, lado, Inches(1))
        sec.header_distance = Inches(0.5)

        normal = self.doc.styles["Normal"]
        normal.font.name = self.fuente
        normal.font.size = Pt(self.tamano)
        normal.font.color.rgb = RGBColor(0, 0, 0)
        poner_fuente(normal.element, self.fuente)
        poner_idioma(normal)
        pf = normal.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.first_line_indent = SANGRIA
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.widow_control = True

        formatos = {
            1: dict(al=WD_ALIGN_PARAGRAPH.CENTER, cursiva=False),
            2: dict(al=WD_ALIGN_PARAGRAPH.LEFT, cursiva=False),
            3: dict(al=WD_ALIGN_PARAGRAPH.LEFT, cursiva=True),
        }
        for nivel, f in formatos.items():
            estilo = self.doc.styles[f"Heading {nivel}"]
            estilo.font.name = self.fuente
            estilo.font.size = Pt(self.tamano)
            estilo.font.bold = True
            estilo.font.italic = f["cursiva"]
            estilo.font.color.rgb = RGBColor(0, 0, 0)
            poner_fuente(estilo.element, self.fuente)
            ef = estilo.paragraph_format
            ef.alignment = f["al"]
            ef.first_line_indent = Inches(0)
            ef.left_indent = Inches(0)
            ef.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            ef.space_before = Pt(0)
            ef.space_after = Pt(0)
            ef.keep_with_next = True

        for nombre in ("List Bullet", "List Number"):
            lf = self.doc.styles[nombre].paragraph_format
            lf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            lf.space_before = Pt(0)
            lf.space_after = Pt(0)

        self._encabezado(sec)

    def _encabezado(self, sec) -> None:
        p = sec.header.paragraphs[0]
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        corto = self.meta.get("titulo_corto", "").strip()
        if corto:
            corto = corto.upper()
            if len(corto) > 50:
                avisos.append(f"El título abreviado tiene {len(corto)} caracteres; APA permite máximo 50.")
            tabs = p.paragraph_format.tab_stops
            # El estilo Header trae un tab centrado a 3,25"; si el título abreviado es corto,
            # el \t caería ahí y el número quedaría en la mitad. Se anulan los tabs del estilo.
            for t in p.style.paragraph_format.tab_stops:
                if t.position != ANCHO_TEXTO:
                    tabs.add_tab_stop(t.position, WD_TAB_ALIGNMENT.CLEAR)
            tabs.add_tab_stop(ANCHO_TEXTO, WD_TAB_ALIGNMENT.RIGHT)
            p.add_run(corto + "\t")
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        campo_pagina(p)

    # ----- párrafos básicos

    def parrafo(self, texto: str = "", *, sangria=True, centrado=False, negrita=False,
                cursiva=False, interlineado=None, tamano=None, junto_siguiente=False):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        if not sangria:
            pf.first_line_indent = Inches(0)
        if centrado:
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if interlineado:
            pf.line_spacing = interlineado
        if junto_siguiente:
            pf.keep_with_next = True
        if texto:
            agregar_texto(p, texto, negrita=negrita, cursiva=cursiva, tamano=tamano)
        return p

    def salto(self) -> None:
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        # El párrafo vacío del salto no debe dejar una línea en blanco arriba de la página nueva.
        self.doc.paragraphs[-1].paragraph_format.line_spacing = Pt(1)

    def titulo(self, texto: str, nivel: int) -> None:
        if re.match(r"^(\d+(\.\d+)*\.?|[IVXLC]+\.|[a-z]\))\s", texto):
            avisos.append(f"El título '{texto}' está numerado; APA no numera los títulos.")
        self.doc.add_paragraph(texto_plano(texto), style=f"Heading {nivel}")

    # ----- portadas

    def logo(self) -> bool:
        """Pone el logo centrado arriba de la portada. `logo: no` lo quita; `logo: ruta` usa otro."""
        valor = str(self.meta.get("logo", "")).strip()
        if valor.lower() in ("no", "false", "ninguno", "0"):
            return False
        logo = Path(valor).expanduser() if valor else LOGO_UMB
        if not logo.is_absolute():
            logo = (self.base / logo).resolve()
        if not logo.exists():
            avisos.append(f"No se encontró el logo en {logo}; la portada queda sin logo.")
            return False
        p = self.parrafo(sangria=False, centrado=True, interlineado=1.0)
        p.add_run().add_picture(str(logo), width=Inches(2.6))
        return True

    def portada_estandar(self) -> None:
        m = self.meta
        hay_logo = self.logo()
        for _ in range(2 if hay_logo else 3):
            self.parrafo(sangria=False)
        self.parrafo(m.get("titulo", "Título del Trabajo"), sangria=False, centrado=True, negrita=True)
        self.parrafo(sangria=False)
        for clave in ("autores", "programa", "materia", "docente", "fecha"):
            valor = m.get(clave) or (fecha_hoy() if clave == "fecha" else "")
            if clave == "autores":
                valor = unir_autores(valor)
            if valor:
                self.parrafo(valor, sangria=False, centrado=True)

    def portada_umb(self) -> None:
        m = self.meta
        interl = 1.5

        def linea(texto=""):
            return self.parrafo(texto, sangria=False, centrado=True, negrita=True, interlineado=interl)

        self.logo()

        for _ in range(2):
            linea()
        linea(m.get("titulo", "Título del Trabajo"))
        linea()
        for autor in dividir(m.get("autores", "")):
            linea(autor)
        for _ in range(4):
            linea()
        if m.get("tutor"):
            linea(m.get("tutor_rotulo", "Tutor del proyecto de investigación"))
            linea(m["tutor"])
            if m.get("tutor_profesion"):
                linea(m["tutor_profesion"])
        else:
            if m.get("docente"):
                linea("Docente")
                linea(m["docente"])
        for _ in range(5):
            linea()
        linea(m.get("universidad", "Universidad Manuela Beltrán"))
        for clave in ("tipo_trabajo", "ciudad"):
            if m.get(clave):
                linea(m[clave])
        linea(m.get("anio", str(dt.date.today().year)))

    # ----- bloques

    def tabla(self, bloque: Bloque, nota: str | None) -> None:
        self.n_tablas += 1
        self.parrafo(f"Tabla {self.n_tablas}", sangria=False, negrita=True, junto_siguiente=True)
        self.parrafo(bloque.texto, sangria=False, cursiva=True, junto_siguiente=True)
        filas = bloque.filas or [[""]]
        columnas = max(len(f) for f in filas)
        t = self.doc.add_table(rows=len(filas), cols=columnas)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        bordes_tabla(t)
        largos, minimos = [], []
        for c in range(columnas):
            textos = [texto_plano(f[c]) for f in filas if c < len(f)]
            prom = sum(len(x) for x in textos[1:]) / max(len(textos) - 1, 1)
            palabra = max((len(w) for x in textos for w in x.split()), default=4)
            largos.append(max(prom, 5))
            minimos.append(min(palabra * 0.085 + 0.2, 2.2))
        total = 6.5
        if sum(minimos) > total:
            minimos = [m * total / sum(minimos) for m in minimos]
        resto = total - sum(minimos)
        pesos = [max(l - m / 0.085, 0) ** 0.8 for l, m in zip(largos, minimos)]
        anchos = [Inches(m + (resto * w / sum(pesos) if sum(pesos) else resto / columnas)) for m, w in zip(minimos, pesos)]
        izquierda = [l > 22 for l in largos]
        for c, col in enumerate(t.columns):
            col.width = int(anchos[c])
        for r in t.rows:
            for c, celda in enumerate(r.cells):
                celda.width = int(anchos[c])
        repetir_cabecera(t.rows[0])
        for r, fila in enumerate(filas):
            for c in range(columnas):
                celda = t.cell(r, c)
                p = celda.paragraphs[0]
                pf = p.paragraph_format
                pf.first_line_indent = Inches(0)
                pf.line_spacing = 1.0
                pf.space_before = Pt(2)
                pf.space_after = Pt(2)
                # Primera columna (etiquetas de fila) a la izquierda; el resto centrado.
                if c > 0 and not izquierda[c]:
                    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if r == 0:
                    pf.keep_with_next = True
                    borde_inferior_celda(celda)
                agregar_texto(p, fila[c] if c < len(fila) else "")
        if nota:
            self.nota(nota)
        else:
            # Línea en blanco entre la tabla y el texto siguiente.
            self.parrafo(sangria=False)

    def figura(self, bloque: Bloque, nota: str | None) -> None:
        self.n_figuras += 1
        self.parrafo(f"Figura {self.n_figuras}", sangria=False, negrita=True, junto_siguiente=True)
        self.parrafo(bloque.texto or "Título de la Figura", sangria=False, cursiva=True, junto_siguiente=True)
        ruta = Path(bloque.ruta).expanduser()
        if not ruta.is_absolute():
            ruta = (self.base / ruta).resolve()
        p = self.parrafo(sangria=False, centrado=True, interlineado=1.0, junto_siguiente=bool(nota))
        if ruta.exists():
            run = p.add_run()
            imagen = run.add_picture(str(ruta))
            if imagen.width > ANCHO_MAX_FIGURA:
                proporcion = ANCHO_MAX_FIGURA / imagen.width
                imagen.width = ANCHO_MAX_FIGURA
                imagen.height = int(imagen.height * proporcion)
        else:
            avisos.append(f"No se encontró la imagen {ruta}; se dejó un marcador.")
            agregar_texto(p, f"[Imagen pendiente: {bloque.ruta}]")
        if nota:
            self.nota(nota)
        else:
            self.parrafo(sangria=False)

    def nota(self, texto: str) -> None:
        p = self.parrafo(sangria=False)
        run = p.add_run("Nota.")
        run.italic = True
        run.font.size = Pt(self.tamano_nota)
        agregar_texto(p, " " + re.sub(r"^\*?Nota\.?\*?\s*", "", texto), tamano=self.tamano_nota)
        self.parrafo(sangria=False)

    def cita_bloque(self, parrafos: list[str]) -> None:
        for n, texto in enumerate(parrafos):
            p = self.parrafo(texto, sangria=n > 0)
            p.paragraph_format.left_indent = SANGRIA

    def codigo(self, lineas: list[str]) -> None:
        for n, linea in enumerate(lineas):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.first_line_indent = Inches(0)
            pf.left_indent = Inches(0.25)
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
            pf.keep_together = True
            if n < len(lineas) - 1 and len(lineas) <= 25:
                pf.keep_with_next = True
            run = p.add_run(linea if linea else " ")
            run.font.size = Pt(8.5)
            poner_fuente(run._element, "Courier New")
            run.font.name = "Courier New"
            ppr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "F2F2F2")
            ppr.append(shd)
        self.parrafo(sangria=False, interlineado=1.0)

    def lista(self, bloque: Bloque) -> None:
        estilo = "List Number" if bloque.ordenada else "List Bullet"
        num_id = None
        if bloque.ordenada:
            numbering = self.doc.part.numbering_part.numbering_definitions._numbering
            base = self.doc.styles["List Number"].element.pPr.numPr.numId.val
            abstract = numbering.num_having_numId(base).abstractNumId.val
            num = numbering.add_num(abstract)
            ov = num.add_lvlOverride(ilvl=0)
            ov.add_startOverride(1)
            num_id = num.numId
        for item in bloque.items:
            p = self.doc.add_paragraph(style=estilo)
            if num_id is not None:
                numpr = p._p.get_or_add_pPr().get_or_add_numPr()
                numpr.get_or_add_ilvl().val = 0
                numpr.get_or_add_numId().val = num_id
            agregar_texto(p, item)

    def referencias(self, entradas: list[str]) -> None:
        for entrada in sorted(entradas, key=clave_orden):
            p = self.parrafo(entrada)
            p.paragraph_format.left_indent = SANGRIA
            p.paragraph_format.first_line_indent = -SANGRIA

    # ----- armado

    def construir(self, bloques: list[Bloque]) -> None:
        if self.meta.get("portada", "estandar").lower().startswith("umb"):
            self.portada_umb()
        else:
            self.portada_estandar()

        secciones = dividir_secciones(bloques)
        resumen = secciones.pop("resumen", None)
        if resumen is not None:
            self.salto()
            self.titulo(resumen[0].texto, 1)
            for b in resumen[1:]:
                if b.tipo != "parrafo":
                    continue
                es_clave = re.match(r"^\*?(Palabras clave|Keywords)", b.texto, re.I)
                self.parrafo(b.texto, sangria=bool(es_clave))

        self.salto()
        self.titulo(self.meta.get("titulo", "Título del Trabajo"), 1)

        cuerpo_texto: list[str] = []
        i = 0
        cuerpo = secciones["cuerpo"]
        while i < len(cuerpo):
            b = cuerpo[i]
            sig = cuerpo[i + 1] if i + 1 < len(cuerpo) else None
            if b.tipo == "titulo":
                nombre = texto_plano(b.texto).strip()
                if b.nivel == 1 and clave_orden(nombre) == "introduccion":
                    avisos.append("Se omitió el título 'Introducción': en APA el título del trabajo hace de introducción.")
                    i += 1
                    continue
                if b.nivel == 1 and clave_orden(nombre).startswith(("referencias", "apendice", "anexo")):
                    self.salto()
                if clave_orden(nombre) == "referencias":
                    self.titulo(nombre, 1)
                    entradas = []
                    i += 1
                    while i < len(cuerpo) and not (cuerpo[i].tipo == "titulo" and cuerpo[i].nivel == 1):
                        if cuerpo[i].tipo == "parrafo":
                            entradas.append(cuerpo[i].texto)
                        elif cuerpo[i].tipo == "lista":
                            entradas.extend(cuerpo[i].items)
                        i += 1
                    self.referencias(entradas)
                    self._revisar_citas(entradas, " ".join(cuerpo_texto))
                    continue
                if b.nivel >= 4:
                    titulo = b.texto.rstrip()
                    if not titulo.endswith((".", "?", "!")):
                        titulo += "."
                    p = self.parrafo()
                    run = p.add_run(texto_plano(titulo))
                    run.bold = True
                    run.italic = b.nivel == 5 or None
                    if sig and sig.tipo == "parrafo":
                        agregar_texto(p, " " + sig.texto)
                        cuerpo_texto.append(sig.texto)
                        i += 1
                    i += 1
                    continue
                self.titulo(b.texto, b.nivel)
            elif b.tipo == "parrafo":
                self.parrafo(b.texto)
                cuerpo_texto.append(b.texto)
            elif b.tipo == "cita":
                self.cita_bloque(b.items)
                cuerpo_texto.extend(b.items)
            elif b.tipo == "lista":
                self.lista(b)
                cuerpo_texto.extend(b.items)
            elif b.tipo in ("tabla", "figura"):
                nota = sig.texto if sig and sig.tipo == "nota" else None
                (self.tabla if b.tipo == "tabla" else self.figura)(b, nota)
                if nota:
                    cuerpo_texto.append(nota)
                    i += 1
            elif b.tipo == "codigo":
                self.codigo(b.items)
            elif b.tipo == "salto":
                self.salto()
            i += 1

        texto_total = " ".join(cuerpo_texto)
        for tipo, n in (("Tabla", self.n_tablas), ("Figura", self.n_figuras)):
            for k in range(1, n + 1):
                if not re.search(rf"\b{tipo} {k}\b", texto_total):
                    avisos.append(f"{tipo} {k} no se menciona en el texto; APA pide nombrarla antes de que aparezca.")

    def _revisar_citas(self, entradas: list[str], cuerpo: str) -> None:
        cuerpo_norm = clave_orden(cuerpo)
        for entrada in entradas:
            plano = texto_plano(entrada)
            m = re.match(r"^(.+?)(?:,|\.\s*\()", plano)
            autor = (m.group(1) if m else plano.split(".")[0]).strip()
            anio = re.search(r"\((\d{4}[a-z]?|s\. f\.)", plano)
            if autor and clave_orden(autor) not in cuerpo_norm:
                avisos.append(f"La referencia de '{autor}' no parece citada en el texto.")
            elif anio and anio.group(1) not in cuerpo:
                avisos.append(f"'{autor}' aparece en el texto, pero no con el año {anio.group(1)}.")

    def guardar(self, salida: Path) -> None:
        self.doc.core_properties.title = texto_plano(self.meta.get("titulo", ""))
        self.doc.core_properties.author = "; ".join(dividir(self.meta.get("autores", "")))
        self.doc.core_properties.language = "es-CO"
        self.doc.save(salida)


# --------------------------------------------------------------------------- auxiliares


def dividir(valor: str) -> list[str]:
    return [a.strip() for a in valor.split(";") if a.strip()]


def unir_autores(valor: str) -> str:
    autores = dividir(valor)
    if len(autores) <= 1:
        return autores[0] if autores else ""
    return ", ".join(autores[:-1]) + " y " + autores[-1]


def fecha_hoy() -> str:
    hoy = dt.date.today()
    return f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"


def dividir_secciones(bloques: list[Bloque]) -> dict[str, list[Bloque]]:
    """Separa la sección 'Resumen' (o 'Abstract') del resto del cuerpo.

    El resumen termina en la línea de palabras clave o, si no la hay, en el siguiente título de nivel 1.
    """
    secciones: dict[str, list[Bloque]] = {"cuerpo": []}
    actual = "cuerpo"
    for b in bloques:
        if b.tipo == "titulo" and b.nivel == 1:
            actual = "resumen" if clave_orden(b.texto) in ("resumen", "abstract") else "cuerpo"
            if actual == "resumen":
                secciones["resumen"] = [b]
                continue
        secciones[actual].append(b)
        if actual == "resumen" and b.tipo == "parrafo" and re.match(
            r"^\*?(Palabras clave|Keywords)", b.texto, re.I
        ):
            actual = "cuerpo"
    return secciones


def exportar_pdf(docx: Path) -> Path | None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        avisos.append("No se encontró LibreOffice; no se generó el PDF.")
        return None
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(docx.parent), str(docx)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    pdf = docx.with_suffix(".pdf")
    return pdf if pdf.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown → .docx en formato APA 7 (guía UMB).")
    ap.add_argument("entrada", type=Path)
    ap.add_argument("-o", "--salida", type=Path)
    ap.add_argument("--pdf", action="store_true", help="exportar también a PDF con LibreOffice")
    args = ap.parse_args()

    entrada = args.entrada.expanduser().resolve()
    meta, cuerpo = leer_metadatos(entrada.read_text(encoding="utf-8"))
    salida = (args.salida or entrada.with_suffix(".docx")).expanduser().resolve()

    documento = DocumentoAPA(meta, entrada.parent)
    documento.construir(leer_bloques(cuerpo))
    documento.guardar(salida)
    print(f"DOCX: {salida}")
    if args.pdf:
        pdf = exportar_pdf(salida)
        if pdf:
            print(f"PDF:  {pdf}")
    for aviso in avisos:
        print(f"AVISO: {aviso}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
