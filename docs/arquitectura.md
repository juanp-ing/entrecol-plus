# Arquitectura de EntreCOL+

## 1. Visión general

EntreCOL+ es una aplicación web con **tres capas desacopladas** (presentación → negocio → datos) y un
**módulo ETL** independiente para la carga masiva de archivos.

```
┌───────────────────────────────────────────────────────────────┐
│ Navegador: HTML + CSS + JS puro, Chart.js, jsPDF              │
└───────────────────────────┬───────────────────────────────────┘
                            │ fetch JSON (cookie de sesión)
┌───────────────────────────▼───────────────────────────────────┐
│ PRESENTACIÓN  backend/app/api/*_routes.py  (Blueprints /api)  │
│   middleware/: auth_required, roles_required, auditoría       │
├───────────────────────────────────────────────────────────────┤
│ NEGOCIO       backend/app/services/*_service.py               │
│   reglas, validaciones, captcha, OAuth, orquestación del ETL  │
├───────────────────────────────────────────────────────────────┤
│ DATOS         backend/app/repositories/*_repository.py        │
│   único lugar con SQL (PyMySQL, consultas parametrizadas)     │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│ MariaDB 10.6+  entrecol_db: tablas, vistas, triggers          │
└───────────────────────────────────────────────────────────────┘

  ETL: backend/app/etl/  extractors → transformers → loaders → MariaDB
       (lo invoca carga_service o un script de scripts/)
```

### Responsabilidades por capa

| Capa | Carpeta | Hace | No hace |
|---|---|---|---|
| Presentación (cliente) | `frontend/` | Formularios, tablas, gráficos, PDF | Reglas de negocio |
| Presentación (API) | `backend/app/api/` | Recibir la petición, validar la forma, llamar al servicio, responder JSON | SQL, llamar repositorios |
| Negocio | `backend/app/services/` | Reglas, cálculos, permisos de dominio, auditoría de acciones | SQL |
| Datos | `backend/app/repositories/` | SQL parametrizado, transacciones | Reglas de negocio |
| ETL | `backend/app/etl/` | Leer, limpiar/normalizar y cargar archivos por lotes | Atender peticiones HTTP |
| Transversal | `middleware/`, `schemas/`, `utils/` | Sesión, roles, auditoría, validaciones, utilidades | — |

## 2. Flujo de una petición

Ejemplo: el usuario pide el reporte de NÓMINA ordenado descendentemente.

1. `frontend/js/pages/reportes/nomina.js` llama a `api.get('/reportes/nomina?orden=DESC')` (`js/api.js`).
2. Flask recibe `GET /api/reportes/nomina`.
3. `middleware/auditoria_middleware.py` (`before_request`) toma el usuario de la sesión y ejecuta
   `SET @app_id_usuario = <id>` en la conexión de la petición.
4. `@auth_required` / `@roles_required` validan sesión y rol (401 / 403 en JSON si fallan).
5. `api/reportes_routes.py` valida la forma de los parámetros (`schemas/validaciones.py`) y llama a
   `reporte_service.reporte_nomina(orden)`.
6. `services/reporte_service.py` aplica la lista blanca de orden, llama a `reporte_repository` y arma
   las tablas y las series para los gráficos. Registra `VER_REPORTE` en `auditoria_accion`.
7. `repositories/reporte_repository.py` ejecuta el SQL sobre `v_empleado_detalle` con PyMySQL.
8. La respuesta vuelve como JSON uniforme (`utils/respuestas.py`).
9. El frontend pinta tablas (`components/tabla.js`) y gráficos (`charts/graficos.js`). Al pulsar
   «Vista previa PDF», `pdf/pdf-generator.js` crea el documento y `pdf/pdf-preview.js` lo muestra en un
   `<iframe>` con `doc.output('bloburl')`; se notifica a la API para auditar `EXPORTAR_PDF`.

Cuando una petición modifica datos (por ejemplo `PUT /api/empleados/<codigo>`), los **triggers** de
MariaDB escriben en `auditoria_datos` el antes y el después, con `@app_id_usuario` como autor.

### Autenticación

- **Local**: usuario + contraseña + token reCAPTCHA v2 → `captcha_service` verifica el token →
  `auth_service` verifica el hash bcrypt, controla intentos fallidos y bloqueo → se crea la sesión.
  Cada intento queda en `auditoria_acceso`.
- **Google**: `google_oauth_service` (Authlib) redirige a Google, valida el `id_token` en el callback y
  vincula el `sub` con `usuario.google_id`.

El captcha está detrás de una interfaz (`captcha_service.py`), así se puede cambiar de proveedor sin
tocar el resto del sistema.

### Carga masiva (ETL)

1. `POST /api/cargas` con el archivo y el tipo de fuente (`NOMINA`, `PELICULAS`, `LIBROS`).
2. `carga_service` guarda el archivo en `data/uploads/`, crea el registro en `carga_archivo` y llama a
   `etl/pipeline.py`.
3. **Extract**: `excel_extractor`, `movies_dat_extractor` o `books_json_extractor`.
4. **Transform**: `nomina_transformer` (normalización a 3FN, periodo por mes de la novedad) o
   `limpieza_entretenimiento`.
5. **Load**: `mariadb_loader` inserta por lotes con `SET @auditoria_desactivada = 1` para no generar
   una fila de auditoría por registro; la carga como tal se audita en `carga_archivo` y `auditoria_accion`.

## 3. Justificación del stack

| Decisión | Justificación |
|---|---|
| **Python** | Un solo lenguaje para la API y el ETL; librerías maduras para Excel (`openpyxl`), JSON y texto; curva de aprendizaje baja para todo el equipo. |
| **Flask** con app factory y Blueprints | Micro-framework sin ORM obligatorio: permite escribir y mostrar el SQL propio (objetivo de la asignatura). Los Blueprints separan los módulos y la factory facilita las pruebas. |
| **API REST JSON** | Desacopla el frontend del backend; cada capa se puede probar por separado. |
| **HTML + CSS + JS puro** | Sin paso de compilación ni dependencias de frameworks; suficiente para formularios, tablas y gráficos. |
| **Chart.js** | Gráficos de torta y barras comparativas con poca configuración; exporta el canvas como imagen para el PDF. |
| **jsPDF + jspdf-autotable** | El PDF se genera en el navegador con los mismos datos ya mostrados; la vista previa en `<iframe>` permite decidir si imprimir, como pide el enunciado. |
| **MariaDB 10.6+** | Compatible con MySQL (motor exigido), soporta `CHECK`, `JSON`, vistas y triggers; libre y fácil de instalar. |
| **PyMySQL** | Conector puro Python, sin dependencias nativas; consultas parametrizadas. |
| **bcrypt** | Hash de contraseñas con sal y costo configurable. |
| **reCAPTCHA v2 + Google OAuth 2.0** | Segundo factor contra ataques automatizados y alternativa de acceso con cuenta institucional. |
| **Triggers + middleware** | Los triggers capturan cualquier cambio de datos aunque se haga fuera de la app; el middleware registra lo que la BD no ve (accesos, reportes, PDF, cargas, consultas). |
