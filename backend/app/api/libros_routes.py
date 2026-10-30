# EntreCOL+ · backend/app/api/libros_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD y búsqueda de libros. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/libros (filtros: título, autor, idioma, rango de fechas; orden; paginación)
#   - GET /api/libros/<id>, POST, PUT, DELETE
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
