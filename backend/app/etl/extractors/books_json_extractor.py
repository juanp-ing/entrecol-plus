# EntreCOL+ · backend/app/etl/extractors/books_json_extractor.py
# Capa: Módulo ETL (independiente de las 3 capas)
# Responsabilidad: Lee Books.json (lista de objetos de libros).
#
# TODO:
#   - Cargar el JSON y validar las claves esperadas (bookID, title, authors, average_rating, isbn, ...)
#   - Ignorar columnas basura como FIELD13
