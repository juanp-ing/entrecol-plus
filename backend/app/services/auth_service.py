# EntreCOL+ · backend/app/services/auth_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Reglas de autenticación local y de sesión.
#
# TODO:
#   - Validar captcha (captcha_service) antes de verificar la contraseña
#   - Verificar contraseña con bcrypt (utils/passwords.py)
#   - Controlar intentos fallidos y bloqueo temporal (bloqueado_hasta)
#   - Rechazar usuarios inactivos; manejar debe_cambiar_password
#   - Registrar cada intento en auditoria_acceso (con su resultado)
#   - Crear y cerrar la sesión; actualizar ultimo_acceso
#   - No contiene SQL: usa los repositorios correspondientes
