# Entregables - Proyecto Final Bases de Datos 2026-2

Según el enunciado *PROYECTO BD - 2026-2* (el video de demostración se entrega por aparte).

| Entregable del enunciado | Archivo |
|---|---|
| Informe Formal de Ingeniería (MER, modelo relacional, conversión a tablas, 3FN, scripts, consultas, decisiones) | `Informe_Ingenieria_EntreCOL.pdf` / `.docx` |
| Manual de Usuario | `Manual_Usuario_EntreCOL.pdf` / `.docx` |
| Archivo SQL de la base de datos finalizada (esquema, 69 triggers y datos) | `entrecol_bd_final.sql` |
| Archivos fuente en ZIP | `entrecol_fuentes.zip` |

## Restaurar la base de datos

```bash
mariadb < entrecol_bd_final.sql      # o: mysql -u root -p < entrecol_bd_final.sql
```

Después se crea el usuario de la aplicación con `db/04_usuario_app.sql`
(o con `sudo ./scripts/instalar_bd.sh`, que toma la contraseña del `.env`).
Las instrucciones para ejecutar la aplicación están en el `README.md` de la raíz.
