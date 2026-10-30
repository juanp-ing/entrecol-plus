# EntreCOL+ · backend/app/api/reportes_routes.py
# Capa: Presentación (API REST / controlador Flask)
# Responsabilidad: Endpoints JSON de los 5 bloques de reportes (datos para tablas y gráficos). Solo recibe la petición, valida la forma de la entrada y llama al servicio.
#
# TODO:
#   - GET /api/reportes/nomina (orden asc/desc de nombres)
#   - GET /api/reportes/informacion-personal/<codigo>
#   - GET /api/reportes/salud-pension (orden asc/desc de nombres)
#   - GET /api/reportes/novedades?desde=MM/AAAA&hasta=MM/AAAA
#   - GET /api/reportes/entretenimiento/... (películas por género, top N libros, top/peor 5 por año, N géneros, frecuencias)
#   - POST /api/reportes/exportado (registrar EXPORTAR_PDF en auditoría)
#   - Definir el Blueprint y sus rutas (sin SQL ni llamadas a repositorios)
#   - Responder con utils/respuestas.py (formato JSON uniforme)
