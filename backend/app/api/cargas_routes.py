# EntreCOL+ · backend/app/api/cargas_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: Carga masiva de archivos (Nómina .xlsx, películas .dat, libros .json) e historial. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - POST /api/cargas (multipart: archivo + tipo_fuente)
#   - GET /api/cargas (historial desde carga_archivo)
#   - GET /api/cargas/<id> (estado, leídos / insertados / rechazados, mensaje)
#   - Validar extensión y tamaño (MAX_UPLOAD_MB)
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
