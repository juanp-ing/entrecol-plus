# EntreCOL+ · backend/app/etl/extractors/movies_dat_extractor.py
# Capa: Módulo ETL (independiente de las 3 capas)
# Responsabilidad: Lee movies.dat (MovieID::Título (Año)::Género1|Género2).
#
# TODO:
#   - Leer línea a línea con la codificación correcta
#   - Separar por '::' y reportar líneas mal formadas
