# EntreCOL+ · backend/app/api/auth_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: Autenticación: login local, login Google, logout y sesión actual. Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - POST /api/auth/login (usuario + contraseña + token reCAPTCHA)
#   - GET /api/auth/google/login y /api/auth/google/callback
#   - POST /api/auth/logout
#   - GET /api/auth/me (usuario y rol de la sesión)
#   - GET /api/auth/captcha-config (site key pública para el frontend)
#   - POST /api/auth/cambiar-password
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
