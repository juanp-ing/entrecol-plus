# EntreCOL+ · backend/app/services/captcha_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Verificación del captcha encapsulada (hoy Google reCAPTCHA v2) para poder cambiar de proveedor.
#
# TODO:
#   - Interfaz verificar(token, ip) -> bool
#   - Implementación reCAPTCHA v2: POST a siteverify con RECAPTCHA_SECRET_KEY (requests)
#   - Implementación falsa para pruebas / desarrollo
#   - No contiene SQL: usa los repositorios correspondientes
