# EntreCOL+ · backend/app/services/usuario_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Reglas de gestión de usuarios y roles.
#
# TODO:
#   - Crear usuario con contraseña hasheada (bcrypt) o solo google_id
#   - Validar unicidad de username y email
#   - Activar / desactivar / desbloquear; restablecer contraseña
#   - No contiene SQL: usa los repositorios correspondientes
