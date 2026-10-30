# EntreCOL+ · backend/app/middleware/auditoria_middleware.py
# Capa: Transversal (middleware Flask)
# Responsabilidad: Auditoría de accesos y acciones en cada petición.
#
# TODO:
#   - before_request: si hay usuario en sesión, ejecutar SET @app_id_usuario = <id> en la conexión
#   - after_request: registrar acciones relevantes (reportes, PDF, cargas, consultas) en auditoria_accion
#   - Capturar IP y user-agent
#   - teardown: limpiar @app_id_usuario
