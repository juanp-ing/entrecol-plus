# CLAUDE.md — EntreCOL+

Contexto para sesiones de Claude Code en este repositorio.

## Proyecto

Proyecto final de Bases de Datos (2026-2): sistema de información de **EntreCOL+** para gestionar
**nómina** (empleados, liquidación mensual, novedades) y una **base de entretenimiento** (películas y libros),
con carga masiva (ETL), autenticación con doble factor, auditoría, CRUD, consultas dinámicas y reportes con
gráficos exportables a PDF.

**Entrega: lunes 18 de noviembre de 2026, 23:55.**

## Stack (no cambiarlo)

- **Backend + ETL**: Python 3.11+, Flask con app factory (`backend/app/__init__.py`) y Blueprints; API REST JSON bajo `/api`.
- **Frontend**: HTML + CSS + JavaScript puro (sin frameworks); gráficos con Chart.js.
- **PDF**: jsPDF + jspdf-autotable en el navegador; vista previa en `<iframe>` con `doc.output('bloburl')`.
- **BD**: MariaDB 10.6+ con PyMySQL.
- **Seguridad**: login local (bcrypt + Google reCAPTCHA v2, encapsulado en `captcha_service.py`) y login con Google OAuth 2.0 (Authlib).
- **Auditoría**: triggers en MariaDB (cambios en datos) + middleware Flask (accesos y acciones).

## Arquitectura de 3 capas

```
frontend ──▶ api/*_routes.py ──▶ services/*_service.py ──▶ repositories/*_repository.py ──▶ MariaDB
(presentación)   (presentación)       (negocio)                  (datos)
                                          └──▶ etl/pipeline.py (extractors → transformers → loaders)
```

### Reglas

1. **El SQL solo vive en `backend/app/repositories/`** (y en `database/`). Nunca en rutas, servicios ni ETL fuera de `etl/loaders/`.
2. **Las rutas no llaman repositorios directamente**: ruta → servicio → repositorio.
3. **Toda acción relevante se audita**: accesos en `auditoria_acceso`, acciones (ver reporte, exportar PDF, cargar archivo, consulta dinámica) en `auditoria_accion`, cambios de datos por triggers en `auditoria_datos`.
4. Consultas siempre parametrizadas (`%s`); orden (`ASC`/`DESC`), columnas y tablas dinámicas solo desde listas blancas.
5. Respuestas JSON uniformes con `utils/respuestas.py`.

## Base de datos `entrecol_db`

Script: `database/schema/entrecol_db.sql` (utf8mb4, `utf8mb4_spanish_ci`, zona horaria -05:00).

### Tablas

- **Nómina**: `dependencia`, `cargo`, `eps`, `arl`, `fondo_pension`, `tipo_novedad`, `periodo` (anio, mes),
  `parametro_nomina` (porcentajes de aportes por clave, p. ej. `PORC_PENSION_EMPLEADO`), `empleado`,
  `nomina_mensual` (una por empleado y periodo), `novedad` (cuelga de `nomina_mensual`).
- **Entretenimiento**: películas, géneros y libros (en el script actual la sección 6 aún está **pendiente**).
- **Seguridad**: `rol`, `usuario` (`password_hash` bcrypt y/o `google_id`; intentos fallidos y bloqueo).
- **Auditoría**: `auditoria_acceso`, `auditoria_accion`, `auditoria_datos`.
- **ETL**: `carga_archivo` (tipo_fuente `NOMINA`/`PELICULAS`/`LIBROS`, contadores y estado).

### Vistas

- `v_empleado_detalle` — empleado con catálogos y aportes de pensión.
- `v_novedad_detalle` — novedad con empleado, dependencia, cargo y periodo (`periodo_txt`, `periodo_fecha`).
- `v_nomina_detalle` — liquidación mensual con devengado y cantidad de novedades.
- `v_pelicula_detalle`, `v_libro_detalle`, `v_libro_ranking_anual` — por crear junto con el módulo de entretenimiento.

### Variables de sesión

- `@app_id_usuario`: el middleware ejecuta `SET @app_id_usuario = <id>` en cada petición; los triggers lo guardan en `auditoria_datos.id_usuario`.
- `@auditoria_desactivada`: las cargas masivas hacen `SET @auditoria_desactivada = 1` (y luego `NULL`) para que los triggers no registren cada fila.

## Decisiones de datos

- Hay **10.681 películas** y **11.127 libros** reales. Las cifras 65.133 y 45.641 del enunciado son los **ID máximos**, no la cantidad de registros.
- Las películas **solo tienen año** (en el título: `Toy Story (1995)`); los filtros por fecha de películas usan **años**.
- Los **periodos de nómina se asignan por el mes de la novedad**.
- El **Top N de libros** debe permitir un **mínimo de votos** (`ratings_count`) para no premiar libros con pocos votos.
- `movies.dat`: `MovieID::Título (Año)::Género1|Género2`. `Books.json`: lista de objetos (`bookID`, `title`,
  `authors` separados por `/`, `average_rating` como texto, `publication_date` en `M/D/AAAA`, columna basura `FIELD13`).
- `backend/app/etl/transformers/limpieza_entretenimiento.py` ya está probado (se copia tal cual desde `insumos/`): no reescribirlo sin motivo.

### Pendiente de agregar desde `insumos/`

- `backend/app/etl/transformers/limpieza_entretenimiento.py`
- `data/normalizado/Nomina_normalizada_3FN.xlsx`
- `docs/diagramas/MER_EntreCOL.drawio`
- Versión de `database/schema/entrecol_db.sql` con el módulo de entretenimiento y sus vistas.

## Reportes del enunciado (5 bloques)

Todos se muestran en el sistema y se exportan a PDF con vista previa.

1. **NÓMINA**: cantidad y lista de empleados; por dependencia; por cargo por dependencia (orden de nombres ASC/DESC elegido por el usuario); torta por dependencia; barras por dependencia por cargo.
2. **INFORMACIÓN PERSONAL**: nombre completo + código, dependencia, cargo, fecha de ingreso (DD/MM/AAAA), EPS, aporte pensión, salario y discriminación de novedades.
3. **SALUD Y PENSIÓN**: frecuencia por EPS y por pensión (empresa); barras por EPS por dependencia y por pensión por dependencia; cantidad y lista por cargo y EPS, y por cargo y pensión.
4. **NOVEDADES**: lista de empleados con novedades entre F1 y F2 (MM/AAAA); cantidad por dependencia y por cargo en ese rango.
5. **BASE-ENTRETENIMIENTO**: películas por género entre F1 y F2; Top N libros por rating; Top 5 mejores y peores libros por año; películas con N géneros; frecuencia de películas por género; frecuencia de libros por año de publicación entre F1 y F2.

Consultas de referencia en `database/queries/reportes/01..05_*.sql`.

## Convenciones

- Código, comentarios y mensajes en **español**.
- `snake_case` en Python y SQL.
- `kebab-case` en nombres de archivos del frontend.
- Commits con **Conventional Commits en español** (`feat: agrega reporte de nómina`).
- Ramas: `main` (entregable), `develop` (integración), `feature/<tema>`.
- Nunca subir `.env` ni `insumos/`.
