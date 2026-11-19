"""Carga los archivos del cliente desde la terminal, con el mismo ETL que usa la pantalla de cargas.

Uso (desde la raiz del proyecto):
    uv run python scripts/cargar_datos.py                 -> carga data/Nomina.xlsx, movies.dat y Books.json
    uv run python scripts/cargar_datos.py libros otro.json
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "backend"))

from app.auditoria import registrar_evento  # noqa: E402
from app.db import conexion  # noqa: E402
from app.etl import libros, nomina, peliculas  # noqa: E402

ORIGENES = {
    "nomina": (nomina, RAIZ / "data" / "Nomina.xlsx"),
    "peliculas": (peliculas, RAIZ / "data" / "movies.dat"),
    "libros": (libros, RAIZ / "data" / "Books.json"),
}


def cargar(nombre: str, ruta: Path) -> None:
    modulo, _ = ORIGENES[nombre]
    datos, resumen = modulo.parsear(ruta.read_bytes())
    with conexion("SISTEMA") as con, con.cursor() as cur:
        modulo.cargar(cur, datos, resumen)
    r = resumen.como_dict()
    registrar_evento("CARGA_ARCHIVO", "SISTEMA",
                     f"{ruta.name} (terminal): {r['insertados']} insertados, {r['actualizados']} actualizados, "
                     f"{r['rechazados']} rechazados")
    print(f"{nombre:10} leidos={r['leidos']:6} insertados={r['insertados']:6} actualizados={r['actualizados']:6} "
          f"sin_cambios={r['sin_cambios']:6} rechazados={r['rechazados']}")
    for a in r["avisos"]:
        print(f"           aviso: {a}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        cargar(sys.argv[1], Path(sys.argv[2]))
    else:
        for n, (_, ruta) in ORIGENES.items():
            cargar(n, ruta)
