# EntreCOL+ · backend/app/api/usuarios_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: CRUD de usuarios del sistema y asignación de roles (solo administrador). Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET/POST /api/usuarios, GET/PUT/DELETE /api/usuarios/<id>
#   - PATCH /api/usuarios/<id>/estado (activar / desactivar / desbloquear)
#   - GET /api/usuarios/roles
#   - Proteger con auth_required + roles_required('ADMIN')
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
