# EntreCOL+ · backend/app/api/empleados_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD de empleados con filtros, orden y paginación. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/empleados (filtros: dependencia, cargo, EPS, pensión; orden asc/desc; paginación)
#   - GET /api/empleados/<codigo> (detalle desde v_empleado_detalle)
#   - POST /api/empleados, PUT /api/empleados/<codigo>, DELETE /api/empleados/<codigo>
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
