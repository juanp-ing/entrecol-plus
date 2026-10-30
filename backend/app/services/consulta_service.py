# EntreCOL+ · backend/app/services/consulta_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Constructor seguro de consultas dinámicas a partir de metadatos.
#
# TODO:
#   - Lista blanca de entidades (vistas), campos y operadores
#   - Construir la especificación de consulta y delegar el SQL parametrizado al repositorio
#   - Límite máximo de filas
#   - Registrar CONSULTA_DINAMICA en auditoria_accion
#   - No contiene SQL: usa los repositorios correspondientes
