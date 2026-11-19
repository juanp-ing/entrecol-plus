"""Pruebas del ETL sin base de datos: validan los hallazgos del analisis de datos del PRD."""
from pathlib import Path

import pytest

from app.etl import libros, nomina, peliculas
from app.etl.comun import ErrorEstructura
from app.reportes.pdf import generar_pdf

DATA = Path(__file__).resolve().parents[1] / "data"


def test_peliculas_archivo_real():
    regs, r = peliculas.parsear((DATA / "movies.dat").read_bytes())
    assert len(regs) == 10681 and not r.rechazados
    toy = next(p for p in regs if p["id"] == 1)
    assert toy["titulo"] == "Toy Story" and toy["anio"] == 1995
    assert "Animation" in toy["generos"]
    sin = [p for p in regs if not p["generos"]]
    assert len(sin) == 1  # "(no genres listed)" se carga sin generos


def test_peliculas_estructura_invalida():
    with pytest.raises(ErrorEstructura):
        peliculas.parsear(b"1,Toy Story,Comedy\n")


def test_peliculas_rechaza_registro_sin_anio():
    regs, r = peliculas.parsear(b"1::Toy Story (1995)::Comedy\n2::Sin anio::Drama\n")
    assert len(regs) == 1 and len(r.rechazados) == 1


def test_libros_archivo_real():
    regs, r = libros.parsear((DATA / "Books.json").read_bytes())
    assert len(regs) == 11127 and not r.rechazados
    realineados = [a for a in r.avisos if "desplazados" in a]
    assert len(realineados) == 4
    b = next(x for x in regs if x["id"] == 12224)
    assert b["autores"] == ["Sam Bass Warner, Jr.", "Sam B. Warner"]
    assert b["isbn13"] == "9780674842113" and b["editorial"] == "Harvard University Press"
    assert max(len(x["autores"]) for x in regs) == 51
    hp = next(x for x in regs if x["id"] == 1)
    assert hp["serie"] == "Harry Potter" and hp["num_serie"] == "6"
    assert len({x["isbn"] for x in regs if x["isbn"]}) == len([x for x in regs if x["isbn"]])


def test_libros_estructura_invalida():
    with pytest.raises(ErrorEstructura):
        libros.parsear(b'[{"id": 1}]')


def test_nomina_archivo_real():
    datos, r = nomina.parsear((DATA / "Nomina.xlsx").read_bytes())
    assert len(datos["empleados"]) == 20 and not r.rechazados
    e = datos["empleados"][0]
    assert (e["ap1"], e["ap2"], e["nombres"]) == ("AGUDELO", "ESCOBAR", "EDWAR DAVID")
    filas = datos["liquidaciones"][0]["filas"]
    assert sum(len(f["novedades"]) for f in filas) == 4
    assert datos["liquidaciones"][0]["periodo"] == (2022, 3)


def test_nomina_periodo_indicado():
    datos, _ = nomina.parsear((DATA / "Nomina.xlsx").read_bytes(), periodo=(2022, 6))
    assert datos["liquidaciones"][0]["periodo"] == (2022, 6)


def test_pdf_generico():
    rep = {"titulo": "Prueba", "parametros": {"Orden": "ASC"}, "secciones": [
        {"tipo": "kpi", "items": [{"etiqueta": "Total", "valor": 3}]},
        {"tipo": "grafico", "titulo": "Torta", "grafico": "pie", "etiquetas": ["A", "B"],
         "series": [{"nombre": "n", "datos": [1, 2]}], "apilado": False},
        {"tipo": "grafico", "titulo": "Barras", "grafico": "bar", "etiquetas": ["A", "B"],
         "series": [{"nombre": "x", "datos": [1, 2]}, {"nombre": "y", "datos": [3, 1]}], "apilado": False},
        {"tipo": "tabla", "titulo": "Tabla", "columnas": ["a", "b"], "filas": [[1, "<b>x</b>"]], "nota": None},
    ]}
    assert generar_pdf(rep, "tester").startswith(b"%PDF")
