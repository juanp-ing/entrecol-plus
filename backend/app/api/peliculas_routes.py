# EntreCOL+ · backend/app/api/peliculas_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD y búsqueda de películas y géneros. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/peliculas (filtros: título, género, rango de años; orden; paginación)
#   - GET /api/peliculas/<id>, POST, PUT, DELETE
#   - GET /api/peliculas/generos
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
