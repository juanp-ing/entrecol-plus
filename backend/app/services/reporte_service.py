# EntreCOL+ · backend/app/services/reporte_service.py
# Capa: Negocio (servicios)
# Responsabilidad: Arma los 5 bloques de reportes: valida parámetros y da forma a tablas y series para gráficos.
#
# TODO:
#   - NÓMINA: totales, listas por dependencia y por cargo-dependencia; series torta y barras
#   - INFORMACIÓN PERSONAL: ficha del empleado + discriminación de novedades
#   - SALUD Y PENSIÓN: frecuencias por EPS / pensión (global y por dependencia); listas por cargo
#   - NOVEDADES: empleados con novedades entre F1 y F2 (MM/AAAA); conteo por dependencia y cargo
#   - ENTRETENIMIENTO: películas por género (años), Top N libros con mínimo de votos, Top/peor 5 por año, películas con N géneros, frecuencias
#   - Validar orden (ASC/DESC) contra lista blanca
#   - Registrar VER_REPORTE en auditoria_accion
#   - No contiene SQL: usa los repositorios correspondientes
