"""Punto de entrada de la API EntreCOL+.

Ejecutar desde la raiz del proyecto:
    uv run uvicorn app.main:app --app-dir backend --reload
La interfaz queda en http://localhost:8000 y la documentacion en http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .auditoria import AuditoriaMiddleware
from .config import RAIZ
from .routers import auth, crud, etl, reportes

app = FastAPI(
    title="EntreCOL+ API",
    description="Sistema de informacion de nomina y catalogo de entretenimiento - ColPlus-Solutions",
    version="0.1.0",
)
app.add_middleware(AuditoriaMiddleware)

app.include_router(auth.router)
app.include_router(crud.router)
app.include_router(etl.router)
app.include_router(reportes.router)


@app.get("/api/salud", tags=["Sistema"])
def salud():
    return {"ok": True}


@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse("/app/login.html")


# Capa de presentacion: archivos estaticos que solo hablan con la API (RNF-07)
app.mount("/app", StaticFiles(directory=RAIZ / "frontend", html=True), name="frontend")
