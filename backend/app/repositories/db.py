# EntreCOL+ · backend/app/repositories/db.py
# Capa: Datos (repositorios; único lugar con SQL)
# Responsabilidad: Conexión a MariaDB con PyMySQL.
#
# TODO:
#   - get_connection() por petición (guardada en flask.g) y cierre en teardown
#   - Ejecutar SET @app_id_usuario = %s al abrir la conexión de una petición autenticada
#   - Cursor DictCursor, charset utf8mb4, autocommit desactivado
#   - Context manager de transacción (commit / rollback)
