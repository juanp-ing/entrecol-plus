# EntreCOL+

Sistema de información para **EntreCOL+**, empresa de entretenimiento multimedia de Colombia.
Proyecto final de **Bases de Datos** (semestre 2026-2). Entrega: **18 de noviembre de 2026**.

El sistema gestiona:

- **Nómina**: empleados, catálogos (dependencia, cargo, EPS, ARL, fondo de pensión), liquidación mensual y novedades (incapacidades y vacaciones).
- **Entretenimiento**: películas (`movies.dat`) y libros (`Books.json`).
- **Carga masiva (ETL)** de archivos Excel, `.dat` y `.json`.
- **Seguridad**: login local (contraseña bcrypt + captcha) y login con Google OAuth 2.0.
- **Auditoría** de accesos, acciones y cambios en los datos.
- **CRUD**, **consultas dinámicas** y **reportes** con gráficos y vista previa / exportación a PDF.

> Estado: estructura base. Los archivos de código solo contienen su encabezado y la lista de TODO.

## Stack

| Parte | Tecnología |
|---|---|
| Backend + ETL | Python 3.11+, Flask (app factory + Blueprints), API REST JSON bajo `/api` |
| Frontend | HTML + CSS + JavaScript puro (sin frameworks), Chart.js |
| PDF | jsPDF + jspdf-autotable en el navegador; vista previa en `<iframe>` con `doc.output('bloburl')` |
| Base de datos | MariaDB 10.6+ (conector PyMySQL) |
| Seguridad | bcrypt, Google reCAPTCHA v2, Google OAuth 2.0 (Authlib) |
| Auditoría | Triggers en MariaDB + middleware Flask |
| Pruebas | pytest |

## Arquitectura

Tres capas desacopladas más un módulo ETL independiente:

```
Frontend (HTML/CSS/JS) ──fetch──▶ api/ (Blueprints) ──▶ services/ (negocio) ──▶ repositories/ (SQL) ──▶ MariaDB
                                                             │
                                                             └──▶ etl/ (extract → transform → load)
```

Detalle en [`docs/arquitectura.md`](docs/arquitectura.md).

## Requisitos

- Python 3.11 o superior
- MariaDB 10.6 o superior
- Credenciales de Google OAuth 2.0 y llaves de reCAPTCHA v2 (opcionales en desarrollo)

## Instalación

```bash
git clone <url-del-repositorio>
cd entrecol-plus

# 1. Entorno virtual y dependencias
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Variables de entorno
cp .env.example .env               # y completar los valores

# 3. Base de datos (¡borra y recrea entrecol_db!)
mariadb -u root -p < database/schema/entrecol_db.sql
```

El script crea un usuario `admin` inicial que debe cambiar su contraseña en el primer ingreso.
Se recomienda crear el usuario de conexión `entrecol_app` (ver la sección 10 del script) en lugar de usar `root`.

## Ejecución

```bash
python run.py
```

La API queda disponible bajo `http://localhost:5000/api` y el frontend en `frontend/index.html`.

## Pruebas

```bash
pytest backend/tests
```

## Estructura

```
entrecol-plus/
├── run.py, config.py          # arranque y configuración
├── backend/
│   ├── app/
│   │   ├── api/               # capa de presentación (Blueprints)
│   │   ├── services/          # capa de negocio
│   │   ├── repositories/      # capa de datos (único lugar con SQL)
│   │   ├── middleware/        # sesión, roles y auditoría
│   │   ├── etl/               # extractors / transformers / loaders
│   │   ├── schemas/           # validaciones de entrada
│   │   └── utils/             # contraseñas, fechas, respuestas JSON
│   └── tests/
├── frontend/                  # index.html (login), pages/, css/, js/
├── database/
│   ├── schema/                # entrecol_db.sql
│   ├── queries/reportes/      # un .sql por bloque de reporte
│   ├── migrations/  seeds/
├── data/
│   ├── samples/               # Nomina.xlsx, movies.dat, Books.json
│   ├── normalizado/           # Nomina_normalizada_3FN.xlsx
│   └── uploads/               # archivos subidos (ignorado por git)
├── docs/                      # arquitectura, diagramas, informe, manual de usuario
└── scripts/
```

## Flujo de trabajo

- `main`: versiones entregables. `develop`: integración. Ramas `feature/<tema>` desde `develop`.
- Commits con [Conventional Commits](https://www.conventionalcommits.org/es/) en español (`feat:`, `fix:`, `docs:`, `chore:` …).

## Equipo

| Integrante | Rol |
|---|---|
| _(por completar)_ | |
| _(por completar)_ | |
| _(por completar)_ | |
| _(por completar)_ | |
