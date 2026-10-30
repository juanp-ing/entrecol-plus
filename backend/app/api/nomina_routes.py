# EntreCOL+ · backend/app/api/nomina_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD de liquidaciones mensuales (nomina_mensual) y periodos. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/nomina?anio=&mes= (desde v_nomina_detalle)
#   - GET /api/nomina/<id>, POST, PUT, DELETE
#   - GET /api/nomina/periodos
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
