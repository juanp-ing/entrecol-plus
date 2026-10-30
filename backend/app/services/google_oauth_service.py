# EntreCOL+ · backend/app/services/google_oauth_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Login con Google OAuth 2.0 / OpenID Connect usando Authlib.
#
# TODO:
#   - Construir la URL de autorización y manejar el callback
#   - Obtener y validar el id_token (claim sub, email, email_verified)
#   - Vincular por google_id o email a un usuario existente y activo
#   - Registrar el acceso (metodo GOOGLE) en auditoria_acceso
#   - No contiene SQL: usa los repositorios correspondientes
