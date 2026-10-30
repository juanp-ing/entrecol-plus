# EntreCOL+ · backend/app/services/novedad_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Reglas de novedades (incapacidades / vacaciones).
#
# TODO:
#   - Validar fecha_fin >= fecha_inicio y días 1..31
#   - Asignar la novedad a la nómina del periodo según el MES de la novedad
#   - Convertir rangos MM/AAAA a fechas (utils/fechas.py)
#   - No contiene SQL: usa los repositorios correspondientes
