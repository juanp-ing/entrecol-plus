# EntreCOL+ · backend/app/__init__.py
# Capa: Arranque (app factory)
# Responsabilidad: Función create_app(): configura Flask, extensiones, middleware y registra los Blueprints.
#
# TODO:
#   - create_app(config_name) que cargue la clase de config.py
#   - Inicializar extensiones (extensions.py)
#   - Registrar el middleware de auditoría (before_request / after_request)
#   - Registrar todos los Blueprints bajo el prefijo /api
#   - Manejadores de error globales que respondan JSON (utils/respuestas.py)
#   - Servir el frontend estático en desarrollo (opcional)
