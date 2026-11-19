-- EntreCOL+ - Usuario de base de datos con privilegios minimos (RNF-02)
-- La aplicacion NO puede crear/alterar/borrar tablas ni modificar la auditoria.
-- La contrasena __APP_PASSWORD__ la reemplaza scripts/instalar_bd.sh con el valor de .env
CREATE USER IF NOT EXISTS 'entrecol_app'@'localhost' IDENTIFIED BY '__APP_PASSWORD__';
ALTER USER 'entrecol_app'@'localhost' IDENTIFIED BY '__APP_PASSWORD__';

-- Tablas de negocio: CRUD completo
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.dependencia      TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.cargo            TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.eps              TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.arl              TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.fondo_pension    TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.periodo          TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.tipo_novedad     TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.parametro_nomina TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.empleado         TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.nomina_mensual   TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.novedad          TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.pelicula         TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.genero           TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.pelicula_genero  TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.editorial        TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.idioma           TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.autor            TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.serie            TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.libro            TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.libro_autor      TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.libro_serie      TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON entrecol.usuario          TO 'entrecol_app'@'localhost';
GRANT SELECT                         ON entrecol.rol              TO 'entrecol_app'@'localhost';

-- Auditoria: solo lectura y escritura de eventos; nunca UPDATE ni DELETE
GRANT SELECT                         ON entrecol.auditoria_datos  TO 'entrecol_app'@'localhost';
GRANT SELECT, INSERT                 ON entrecol.auditoria_evento TO 'entrecol_app'@'localhost';

FLUSH PRIVILEGES;
