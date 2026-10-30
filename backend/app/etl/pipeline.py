# EntreCOL+ · backend/app/etl/pipeline.py
# Capa: Módulo ETL (independiente de las 3 capas)
# Responsabilidad: Orquesta extracción -> transformación -> carga para cada tipo de fuente.
#
# TODO:
#   - ejecutar_carga(tipo_fuente, ruta_archivo) -> resumen (leídos, insertados, rechazados, errores)
#   - Elegir extractor / transformer según NOMINA, PELICULAS o LIBROS
#   - Usable desde la API (carga_service) y desde línea de comandos (scripts/)
