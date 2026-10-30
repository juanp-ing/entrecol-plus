# EntreCOL+ · backend/app/services/carga_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Orquesta una carga masiva: guarda el archivo, ejecuta el pipeline ETL y registra el resultado.
#
# TODO:
#   - Guardar el archivo en data/uploads con nombre seguro
#   - Crear el registro en carga_archivo (EN_PROCESO)
#   - Invocar etl/pipeline.py según tipo_fuente (NOMINA, PELICULAS, LIBROS)
#   - Actualizar contadores y estado final (COMPLETADA, CON_ERRORES, FALLIDA)
#   - Registrar CARGAR_ARCHIVO en auditoria_accion
#   - No contiene SQL: usa los repositorios correspondientes
