# EntreCOL+ · backend/app/api/auditoria_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: Consulta de las bitácoras de auditoría (accesos, acciones y cambios en datos). Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/auditoria/accesos (filtros: usuario, resultado, fechas)
#   - GET /api/auditoria/acciones (filtros: usuario, módulo, acción, fechas)
#   - GET /api/auditoria/datos (filtros: tabla, operación, fechas)
#   - Proteger con roles_required('ADMIN')
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
