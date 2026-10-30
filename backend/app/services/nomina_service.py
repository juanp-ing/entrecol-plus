# EntreCOL+ · backend/app/services/nomina_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Reglas de liquidación mensual.
#
# TODO:
#   - Crear el periodo (año, mes) si no existe
#   - Validar dias_trabajados (0..31), bonificación y transporte >= 0
#   - Una liquidación por empleado y periodo
#   - Calcular devengado y aportes con parametro_nomina (sin valores quemados)
#   - No contiene SQL: usa los repositorios correspondientes
