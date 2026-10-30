# EntreCOL+ · backend/app/api/novedades_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD de novedades (incapacidades, vacaciones) asociadas a una liquidación. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/novedades (filtro por rango MM/AAAA, empleado, tipo)
#   - GET /api/novedades/<id>, POST, PUT, DELETE
#   - GET /api/novedades/tipos
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
