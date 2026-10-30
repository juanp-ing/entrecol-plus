# EntreCOL+ · backend/app/api/consultas_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: Consultas dinámicas construidas por el usuario (sin SQL libre). Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/consultas/metadatos (entidades, campos y operadores permitidos)
#   - POST /api/consultas/ejecutar (entidad, campos, filtros, orden, límite)
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
