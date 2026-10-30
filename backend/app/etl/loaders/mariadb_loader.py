# EntreCOL+ · backend/app/etl/loaders/mariadb_loader.py
# Capa: Módulo ETL (independiente de las 3 capas)
# Responsabilidad: Inserta los datos transformados en MariaDB por lotes.
#
# TODO:
#   - SET @auditoria_desactivada = 1 durante la carga y restaurarlo al final
#   - executemany por lotes dentro de una transacción
#   - Upsert de catálogos y control de duplicados
#   - Devolver contadores de insertados / rechazados
