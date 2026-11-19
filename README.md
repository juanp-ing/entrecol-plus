# EntreCOL+

Sistema de información web para la nómina y el catálogo de entretenimiento de EntreCOL+ (ColPlus-Solutions).
Proyecto final de Bases de Datos, UMB, 2026-2. Los requisitos están en el PRD (`prd-entrecol-logo.docx`).

**Stack:** HTML/CSS/JS + Chart.js · Python + FastAPI · PyMySQL con SQL escrito a mano · pandas/openpyxl · MariaDB · bcrypt · OAuth 2.0 + JWT · ReportLab + matplotlib.

## Entregables

La carpeta [`entregables/`](entregables/) reúne lo que pide el enunciado: informe de ingeniería y manual de usuario (PDF y Word), el archivo SQL de la base finalizada y los fuentes en ZIP.

## Puesta en marcha

```bash
cp .env.example .env               # ajustar DB_PASSWORD y JWT_SECRET (ya viene un .env generado)
uv sync                            # instala dependencias en .venv
sudo ./scripts/instalar_bd.sh      # crea la BD, tablas, triggers y el usuario de mínimos privilegios
                                   # (--recrear borra la base y la crea de nuevo)
uv run python scripts/crear_admin.py              # usuario ADMINISTRADOR
uv run python scripts/crear_admin.py gerente "Gerente" CONSULTA
uv run uvicorn app.main:app --app-dir backend --reload
```

- Interfaz: http://localhost:8000 · Documentación de la API: http://localhost:8000/docs
- Primera carga: entrar como administrador → **Carga de archivos** → subir `data/Nomina.xlsx`, `data/movies.dat` y `data/Books.json`.
- Pruebas: `uv run pytest`

## Estructura

```
db/
  01_esquema.sql        21 tablas (nómina + entretenimiento), colación utf8mb4_unicode_ci para MariaDB
  02_seguridad.sql      rol, usuario, auditoria_datos, auditoria_evento
  03_triggers.sql       69 triggers de auditoría (GENERADO por scripts/generar_triggers.py)
  04_usuario_app.sql    usuario entrecol_app: CRUD en tablas de negocio, sin DDL, auditoría solo lectura
backend/app/
  main.py               FastAPI + archivos estáticos del frontend
  db.py                 conexión PyMySQL; fija @app_user en cada conexión para los triggers
  seguridad.py          bcrypt, JWT, dependencias de rol
  captcha.py            captcha local (imagen) o reCAPTCHA v2 (CAPTCHA_MODO en .env)
  auditoria.py          middleware y registro de eventos (logins, accesos, reportes, cargas)
  entidades.py          catálogo de entidades del CRUD (lista blanca de tablas/columnas)
  etl/                  peliculas.py, libros.py, nomina.py (parsear = validar/limpiar, cargar = upsert)
  reportes/consultas.py SQL de los 5 grupos de reportes + auditoría
  reportes/pdf.py       PDF con ReportLab + gráficos matplotlib
  routers/              auth, crud, etl, reportes
frontend/               login.html, index.html, css/, js/ (SPA sin compilación)
scripts/                instalar_bd.sh, crear_admin.py, generar_triggers.py
data/                   archivos originales del cliente
tests/                  pruebas del ETL y del PDF
```

## Trazabilidad con el PRD

| Requisito | Dónde |
|---|---|
| RF-01 a RF-04 | `routers/auth.py`, `seguridad.py`, `captcha.py` |
| RF-05 a RF-10 | `etl/`, `routers/etl.py` (una transacción por carga, upsert, resumen) |
| RF-11 | `entidades.py`, `routers/crud.py` |
| RF-12 a RF-14 | `reportes/consultas.py`, `reportes/pdf.py`, `frontend/js/reportes.js` |
| RF-15 | `db/03_triggers.sql` + `SET @app_user` en `db.py` |
| RF-16, RF-17 | `auditoria.py`, reporte `/api/reportes/auditoria` (solo admin) |
| RNF-01 | todas las consultas usan `%s`; identificadores solo desde listas blancas |
| RNF-02 | `db/04_usuario_app.sql` |
| RNF-04 | listados paginados, índices en `01_esquema.sql` |

## Decisiones tomadas en la base (confirmar con el equipo)

- **Período de nómina:** la hoja de liquidación no indica el mes. El ETL lo toma del nombre de la hoja (`2022-03`), del año/mes que se escribe al cargar, o, si no hay ninguno, del mes de la novedad más antigua (03/2022 con el archivo actual).
- **ISBN repetido (hallazgo 3 del PRD):** era un efecto de los 4 libros desplazados: el valor `3.58` caía en la columna ISBN. Una vez realineados, no queda ningún duplicado. Si en otro archivo aparece un duplicado real, el libro se rechaza y se informa el motivo.
- **Fechas imposibles** (`11/31/2000`, `6/31/1982`): el libro se carga sin fecha y queda un aviso en el resumen.
- **Recargas:** los triggers solo auditan los UPDATE que cambian algún valor, y las relaciones se reescriben solo si cambiaron.
- **Nombre del empleado:** las dos primeras palabras son los apellidos y el resto, los nombres.
