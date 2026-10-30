# EntreCOL+ · backend/app/middleware/auth_required.py
# Capa: Transversal (middleware Flask)
# Responsabilidad: Decorador que exige una sesión válida.
#
# TODO:
#   - Verificar la sesión; responder 401 JSON si no existe
#   - Cargar el usuario actual en flask.g
