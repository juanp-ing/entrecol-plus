# EntreCOL+ · backend/app/api/catalogos_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD genérico de catálogos: dependencia, cargo, EPS, ARL, fondo de pensión, tipo de novedad. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/catalogos/<catalogo> y GET /api/catalogos/<catalogo>/<id>
#   - POST / PUT / DELETE sobre /api/catalogos/<catalogo>
#   - Validar <catalogo> contra una lista blanca
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
