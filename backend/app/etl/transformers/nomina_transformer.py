# EntreCOL+ · backend/app/etl/transformers/nomina_transformer.py
# Capa: Módulo ETL (independiente de las 3 capas)
# Responsabilidad: Normaliza los datos de nómina a 3FN (catálogos, empleado, nómina, novedad).
#
# TODO:
#   - Normalizar texto (mayúsculas, espacios, tildes) de catálogos
#   - Convertir fechas y montos
#   - Asignar cada novedad al periodo según su MES
#   - Separar registros válidos y rechazados con motivo
