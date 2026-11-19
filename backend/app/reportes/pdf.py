"""Convierte el diccionario de un reporte en PDF con ReportLab + matplotlib (RF-14)."""
import io
from datetime import datetime
from decimal import Decimal

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import landscape, letter  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

PALETA = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
          "#f97316", "#6366f1", "#14b8a6", "#a855f7", "#eab308", "#64748b", "#0ea5e9", "#d946ef"]
AZUL = colors.HexColor("#1e3a8a")

_est = getSampleStyleSheet()
EST_TITULO = ParagraphStyle("t", parent=_est["Title"], textColor=AZUL, fontSize=18)
EST_H2 = ParagraphStyle("h2", parent=_est["Heading2"], textColor=AZUL, spaceBefore=10)
EST_CELDA = ParagraphStyle("c", parent=_est["BodyText"], fontSize=7.5, leading=9)
EST_NOTA = ParagraphStyle("n", parent=_est["BodyText"], fontSize=8, textColor=colors.grey)


def _fmt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (float, Decimal)):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(v)


def _grafico(s: dict, ancho_cm: float) -> Image:
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=130)
    if s["grafico"] == "pie":
        datos = s["series"][0]["datos"]
        ax.pie(datos, labels=s["etiquetas"], autopct=lambda p: f"{p:.0f}%" if p >= 3 else "",
               colors=PALETA[: len(datos)], startangle=90, textprops={"fontsize": 8})
        ax.axis("equal")
    else:
        n = len(s["series"])
        x = range(len(s["etiquetas"]))
        ancho = 0.8 / (1 if s.get("apilado") else max(n, 1))
        base = [0] * len(s["etiquetas"])
        for i, serie in enumerate(s["series"]):
            color = PALETA[i % len(PALETA)]
            if s.get("apilado"):
                ax.bar(x, serie["datos"], 0.8, bottom=base, label=serie["nombre"], color=color)
                base = [a + b for a, b in zip(base, serie["datos"])]
            else:
                ax.bar([xi - 0.4 + ancho * (i + 0.5) for xi in x], serie["datos"], ancho, label=serie["nombre"], color=color)
        ax.set_xticks(list(x))
        rot = 45 if len(s["etiquetas"]) > 6 else 0
        ax.set_xticklabels(s["etiquetas"], rotation=rot, ha="right" if rot else "center", fontsize=7)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3)
        if n > 1:
            ax.legend(fontsize=7, ncols=min(n, 4), frameon=False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=ancho_cm * cm, height=ancho_cm * cm * 4.2 / 9)


def _tabla(s: dict, ancho_util: float) -> Table:
    filas = [[Paragraph(f"<b>{c}</b>", EST_CELDA) for c in s["columnas"]]]
    filas += [[Paragraph(_fmt(v).replace("&", "&amp;").replace("<", "&lt;"), EST_CELDA) for v in f] for f in s["filas"]]
    t = Table(filas, repeatRows=1, colWidths=[ancho_util / len(s["columnas"])] * len(s["columnas"]))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def generar_pdf(reporte: dict, usuario: str) -> bytes:
    buf = io.BytesIO()
    tam = landscape(letter)
    doc = SimpleDocTemplate(buf, pagesize=tam, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm, title=reporte["titulo"], author="EntreCOL+")
    ancho_util = tam[0] - 3 * cm
    historia = [
        Paragraph(f"EntreCOL+ &middot; {reporte['titulo']}", EST_TITULO),
        Paragraph(" &nbsp;|&nbsp; ".join(f"<b>{k}:</b> {v}" for k, v in reporte.get("parametros", {}).items()), EST_NOTA),
        Spacer(1, 0.4 * cm),
    ]
    for s in reporte["secciones"]:
        if s["tipo"] == "kpi":
            t = Table([[Paragraph(f"<font size=8 color='#64748b'>{i['etiqueta']}</font><br/>"
                                  f"<font size=16 color='#1e3a8a'><b>{_fmt(i['valor'])}</b></font>", EST_CELDA)
                        for i in s["items"]]])
            t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                                   ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                                   ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
            historia.append(t)
        elif s["tipo"] == "grafico":
            historia += [Paragraph(s["titulo"], EST_H2)]
            if s["etiquetas"]:
                historia.append(_grafico(s, 22))
            else:
                historia.append(Paragraph("Sin datos para graficar.", EST_NOTA))
        elif s["tipo"] == "tabla":
            historia.append(Paragraph(f"{s['titulo']} ({len(s['filas'])})", EST_H2))
            if s["filas"]:
                historia.append(_tabla(s, ancho_util))
            if s.get("nota"):
                historia.append(Paragraph(s["nota"], EST_NOTA))
        historia.append(Spacer(1, 0.3 * cm))

    generado = datetime.now().strftime("%d/%m/%Y %H:%M")

    def pie(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawString(1.5 * cm, 0.8 * cm, f"Generado por {usuario} el {generado}")
        canvas.drawRightString(tam[0] - 1.5 * cm, 0.8 * cm, f"Pagina {d.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()
