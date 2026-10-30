-- =====================================================================
--  EntreCOL+  ·  Sistema de Información de Nómina y Entretenimiento
--  Script de creación de la base de datos (MariaDB 10.6+ / compatible MySQL 8)
--  Generado: 2026-10-29
--  Contenido:
--    1. Base de datos
--    2. Módulo NÓMINA (catálogos, empleado, periodo, nómina mensual, novedad)
--    3. Módulo SEGURIDAD (rol, usuario: login local bcrypt + Google OAuth 2.0)
--    4. Módulo AUDITORÍA (accesos y acciones vía middleware; datos vía triggers)
--    5. Módulo ETL (registro de cargas de archivos)
--    6. Módulo ENTRETENIMIENTO (pendiente: estructura de .dat y .json)
--    7. Triggers de auditoría
--    8. Vistas para reportes
--    9. Datos iniciales
-- =====================================================================

SET NAMES utf8mb4;

-- ¡ATENCIÓN! Borra y recrea la base de datos completa.
DROP DATABASE IF EXISTS entrecol_db;
CREATE DATABASE entrecol_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_spanish_ci;   -- ordena la Ñ y las tildes como en español
USE entrecol_db;

SET time_zone = '-05:00';       -- America/Bogota

-- =====================================================================
-- 2. MÓDULO NÓMINA
-- =====================================================================

CREATE TABLE dependencia (
  id_dependencia      INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_dependencia  VARCHAR(80)   NOT NULL,
  CONSTRAINT pk_dependencia PRIMARY KEY (id_dependencia),
  CONSTRAINT uq_dependencia_nombre UNIQUE (nombre_dependencia)
) ENGINE=InnoDB COMMENT='Áreas de la empresa';

CREATE TABLE cargo (
  id_cargo      INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_cargo  VARCHAR(80)   NOT NULL,
  CONSTRAINT pk_cargo PRIMARY KEY (id_cargo),
  CONSTRAINT uq_cargo_nombre UNIQUE (nombre_cargo)
) ENGINE=InnoDB COMMENT='Catálogo de cargos (independiente de la dependencia)';

CREATE TABLE eps (
  id_eps      INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_eps  VARCHAR(80)   NOT NULL,
  CONSTRAINT pk_eps PRIMARY KEY (id_eps),
  CONSTRAINT uq_eps_nombre UNIQUE (nombre_eps)
) ENGINE=InnoDB COMMENT='Entidades Promotoras de Salud';

CREATE TABLE arl (
  id_arl      INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_arl  VARCHAR(80)   NOT NULL,
  CONSTRAINT pk_arl PRIMARY KEY (id_arl),
  CONSTRAINT uq_arl_nombre UNIQUE (nombre_arl)
) ENGINE=InnoDB COMMENT='Administradoras de Riesgos Laborales';

CREATE TABLE fondo_pension (
  id_fondo_pension  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_fondo      VARCHAR(80)   NOT NULL,
  CONSTRAINT pk_fondo_pension PRIMARY KEY (id_fondo_pension),
  CONSTRAINT uq_fondo_nombre UNIQUE (nombre_fondo)
) ENGINE=InnoDB COMMENT='Fondos de pensión';

CREATE TABLE tipo_novedad (
  id_tipo_novedad  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_tipo      VARCHAR(40)   NOT NULL,
  CONSTRAINT pk_tipo_novedad PRIMARY KEY (id_tipo_novedad),
  CONSTRAINT uq_tipo_novedad_nombre UNIQUE (nombre_tipo)
) ENGINE=InnoDB COMMENT='INCAPACIDAD, VACACIONES, ...';

CREATE TABLE periodo (
  id_periodo  INT UNSIGNED       NOT NULL AUTO_INCREMENT,
  anio        SMALLINT UNSIGNED  NOT NULL,
  mes         TINYINT UNSIGNED   NOT NULL,
  CONSTRAINT pk_periodo PRIMARY KEY (id_periodo),
  CONSTRAINT uq_periodo UNIQUE (anio, mes),
  CONSTRAINT ck_periodo_mes  CHECK (mes BETWEEN 1 AND 12),
  CONSTRAINT ck_periodo_anio CHECK (anio BETWEEN 1990 AND 2100)
) ENGINE=InnoDB COMMENT='Mes de liquidación de nómina';

CREATE TABLE parametro_nomina (
  id_parametro  INT UNSIGNED   NOT NULL AUTO_INCREMENT,
  clave         VARCHAR(50)    NOT NULL,
  valor         DECIMAL(10,4)  NOT NULL,
  descripcion   VARCHAR(200)   NULL,
  CONSTRAINT pk_parametro_nomina PRIMARY KEY (id_parametro),
  CONSTRAINT uq_parametro_clave UNIQUE (clave)
) ENGINE=InnoDB COMMENT='Porcentajes de aportes; evita valores quemados en las consultas';

CREATE TABLE empleado (
  codigo_empleado   INT UNSIGNED   NOT NULL,
  primer_apellido   VARCHAR(50)    NOT NULL,
  segundo_apellido  VARCHAR(50)    NULL,
  nombres           VARCHAR(80)    NOT NULL,
  fecha_ingreso     DATE           NOT NULL,
  salario           DECIMAL(12,2)  NOT NULL,
  id_dependencia    INT UNSIGNED   NOT NULL,
  id_cargo          INT UNSIGNED   NOT NULL,
  id_eps            INT UNSIGNED   NOT NULL,
  id_arl            INT UNSIGNED   NOT NULL,
  id_fondo_pension  INT UNSIGNED   NOT NULL,
  CONSTRAINT pk_empleado PRIMARY KEY (codigo_empleado),
  CONSTRAINT fk_empleado_dependencia FOREIGN KEY (id_dependencia)
    REFERENCES dependencia (id_dependencia) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_cargo FOREIGN KEY (id_cargo)
    REFERENCES cargo (id_cargo) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_eps FOREIGN KEY (id_eps)
    REFERENCES eps (id_eps) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_arl FOREIGN KEY (id_arl)
    REFERENCES arl (id_arl) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_fondo FOREIGN KEY (id_fondo_pension)
    REFERENCES fondo_pension (id_fondo_pension) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_empleado_salario CHECK (salario > 0),
  INDEX ix_empleado_nombre (primer_apellido, segundo_apellido, nombres)
) ENGINE=InnoDB COMMENT='Información general del empleado';

CREATE TABLE nomina_mensual (
  id_nomina        INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  codigo_empleado  INT UNSIGNED      NOT NULL,
  id_periodo       INT UNSIGNED      NOT NULL,
  dias_trabajados  TINYINT UNSIGNED  NOT NULL,
  bonificacion     DECIMAL(12,2)     NOT NULL DEFAULT 0,
  transporte       DECIMAL(12,2)     NOT NULL DEFAULT 0,
  CONSTRAINT pk_nomina_mensual PRIMARY KEY (id_nomina),
  CONSTRAINT uq_nomina_empleado_periodo UNIQUE (codigo_empleado, id_periodo),
  CONSTRAINT fk_nomina_empleado FOREIGN KEY (codigo_empleado)
    REFERENCES empleado (codigo_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_nomina_periodo FOREIGN KEY (id_periodo)
    REFERENCES periodo (id_periodo) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_nomina_dias CHECK (dias_trabajados BETWEEN 0 AND 31),
  CONSTRAINT ck_nomina_bonif CHECK (bonificacion >= 0),
  CONSTRAINT ck_nomina_transp CHECK (transporte >= 0)
) ENGINE=InnoDB COMMENT='Liquidación mensual por empleado';

CREATE TABLE novedad (
  id_novedad       INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  id_nomina        INT UNSIGNED      NOT NULL,
  id_tipo_novedad  INT UNSIGNED      NOT NULL,
  fecha_inicio     DATE              NOT NULL,
  fecha_fin        DATE              NOT NULL,
  dias             TINYINT UNSIGNED  NOT NULL,
  CONSTRAINT pk_novedad PRIMARY KEY (id_novedad),
  CONSTRAINT fk_novedad_nomina FOREIGN KEY (id_nomina)
    REFERENCES nomina_mensual (id_nomina) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_novedad_tipo FOREIGN KEY (id_tipo_novedad)
    REFERENCES tipo_novedad (id_tipo_novedad) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_novedad_fechas CHECK (fecha_fin >= fecha_inicio),
  CONSTRAINT ck_novedad_dias   CHECK (dias BETWEEN 1 AND 31),
  INDEX ix_novedad_fechas (fecha_inicio, fecha_fin)
) ENGINE=InnoDB COMMENT='Incapacidades y vacaciones de cada liquidación';

-- =====================================================================
-- 3. MÓDULO SEGURIDAD
--    Login local: password_hash (bcrypt) + captcha (validado en Flask)
--    Login Google: google_id (claim "sub" de OAuth 2.0 / OpenID Connect)
-- =====================================================================

CREATE TABLE rol (
  id_rol       INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre_rol   VARCHAR(30)   NOT NULL,
  descripcion  VARCHAR(200)  NULL,
  CONSTRAINT pk_rol PRIMARY KEY (id_rol),
  CONSTRAINT uq_rol_nombre UNIQUE (nombre_rol)
) ENGINE=InnoDB;

CREATE TABLE usuario (
  id_usuario             INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  username               VARCHAR(50)       NOT NULL,
  email                  VARCHAR(120)      NOT NULL,
  nombre_completo        VARCHAR(120)      NOT NULL,
  password_hash          VARCHAR(255)      NULL     COMMENT 'bcrypt ($2b$...). NULL si solo usa Google',
  google_id              VARCHAR(64)       NULL     COMMENT 'Claim sub de Google. NULL si solo usa login local',
  id_rol                 INT UNSIGNED      NOT NULL,
  activo                 BOOLEAN           NOT NULL DEFAULT TRUE,
  debe_cambiar_password  BOOLEAN           NOT NULL DEFAULT FALSE,
  intentos_fallidos      TINYINT UNSIGNED  NOT NULL DEFAULT 0,
  bloqueado_hasta        DATETIME          NULL,
  ultimo_acceso          DATETIME          NULL,
  fecha_creacion         DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),
  CONSTRAINT uq_usuario_username UNIQUE (username),
  CONSTRAINT uq_usuario_email UNIQUE (email),
  CONSTRAINT uq_usuario_google UNIQUE (google_id),
  CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol)
    REFERENCES rol (id_rol) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_usuario_metodo CHECK (password_hash IS NOT NULL OR google_id IS NOT NULL)
) ENGINE=InnoDB COMMENT='Usuarios del sistema';

-- =====================================================================
-- 4. MÓDULO AUDITORÍA
-- =====================================================================

-- 4.1 Accesos (lo escribe el middleware de Flask en cada intento de login/logout)
CREATE TABLE auditoria_acceso (
  id_acceso           BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  id_usuario          INT UNSIGNED     NULL,
  username_intentado  VARCHAR(120)     NOT NULL,
  metodo              ENUM('LOCAL','GOOGLE')  NOT NULL,
  evento              ENUM('LOGIN','LOGOUT')  NOT NULL DEFAULT 'LOGIN',
  resultado           ENUM('EXITOSO','PASSWORD_INVALIDO','CAPTCHA_INVALIDO',
                           'USUARIO_INEXISTENTE','USUARIO_BLOQUEADO','USUARIO_INACTIVO',
                           'GOOGLE_RECHAZADO') NOT NULL,
  ip                  VARCHAR(45)      NULL,
  user_agent          VARCHAR(255)     NULL,
  fecha               DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_auditoria_acceso PRIMARY KEY (id_acceso),
  CONSTRAINT fk_aud_acceso_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
  INDEX ix_aud_acceso_fecha (fecha)
) ENGINE=InnoDB COMMENT='Bitácora de autenticación';

-- 4.2 Acciones de aplicación (middleware: reportes, PDF, cargas, consultas dinámicas)
CREATE TABLE auditoria_accion (
  id_accion   BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  id_usuario  INT UNSIGNED     NULL,
  accion      VARCHAR(40)      NOT NULL COMMENT 'VER_REPORTE, EXPORTAR_PDF, CARGAR_ARCHIVO, CONSULTA_DINAMICA, ...',
  modulo      VARCHAR(40)      NOT NULL COMMENT 'NOMINA, SALUD_PENSION, NOVEDADES, ENTRETENIMIENTO, SEGURIDAD',
  detalle     JSON             NULL     COMMENT 'Parámetros usados (filtros, fechas, N, orden)',
  ip          VARCHAR(45)      NULL,
  fecha       DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_auditoria_accion PRIMARY KEY (id_accion),
  CONSTRAINT fk_aud_accion_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
  INDEX ix_aud_accion_fecha (fecha)
) ENGINE=InnoDB COMMENT='Bitácora de uso de la aplicación';

-- 4.3 Cambios en los datos (la escriben los TRIGGERS)
--     Flask debe ejecutar  SET @app_id_usuario = <id>;  al abrir cada conexión/petición
CREATE TABLE auditoria_datos (
  id_auditoria      BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  tabla             VARCHAR(64)      NOT NULL,
  operacion         ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  id_registro       VARCHAR(64)      NOT NULL,
  datos_anteriores  JSON             NULL,
  datos_nuevos      JSON             NULL,
  id_usuario        INT UNSIGNED     NULL     COMMENT 'Usuario de la aplicación (@app_id_usuario)',
  usuario_bd        VARCHAR(100)     NOT NULL COMMENT 'Usuario de MariaDB (CURRENT_USER)',
  fecha             DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_auditoria_datos PRIMARY KEY (id_auditoria),
  CONSTRAINT fk_aud_datos_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
  INDEX ix_aud_datos_tabla (tabla, fecha)
) ENGINE=InnoDB COMMENT='Historial de INSERT/UPDATE/DELETE';

-- =====================================================================
-- 5. MÓDULO ETL
-- =====================================================================

CREATE TABLE carga_archivo (
  id_carga              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  id_usuario            INT UNSIGNED  NULL,
  tipo_fuente           ENUM('NOMINA','PELICULAS','LIBROS') NOT NULL,
  nombre_archivo        VARCHAR(255)  NOT NULL,
  registros_leidos      INT UNSIGNED  NOT NULL DEFAULT 0,
  registros_insertados  INT UNSIGNED  NOT NULL DEFAULT 0,
  registros_rechazados  INT UNSIGNED  NOT NULL DEFAULT 0,
  estado                ENUM('EN_PROCESO','COMPLETADA','CON_ERRORES','FALLIDA') NOT NULL DEFAULT 'EN_PROCESO',
  mensaje               TEXT          NULL,
  fecha_inicio          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_fin             DATETIME      NULL,
  CONSTRAINT pk_carga_archivo PRIMARY KEY (id_carga),
  CONSTRAINT fk_carga_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Bitácora de cargas masivas';

-- =====================================================================
-- 6. MÓDULO ENTRETENIMIENTO
--    PENDIENTE: se define al revisar el README de los .dat (películas)
--    y la estructura del .json (libros).
-- =====================================================================

-- =====================================================================
-- 7. TRIGGERS DE AUDITORÍA
--    Se desactivan en cargas masivas con:  SET @auditoria_desactivada = 1;
-- =====================================================================
DELIMITER $$
CREATE TRIGGER trg_empleado_ains
AFTER INSERT ON empleado FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('empleado', 'INSERT', NEW.codigo_empleado, NULL, JSON_OBJECT('codigo_empleado', NEW.codigo_empleado, 'primer_apellido', NEW.primer_apellido, 'segundo_apellido', NEW.segundo_apellido, 'nombres', NEW.nombres, 'fecha_ingreso', NEW.fecha_ingreso, 'salario', NEW.salario, 'id_dependencia', NEW.id_dependencia, 'id_cargo', NEW.id_cargo, 'id_eps', NEW.id_eps, 'id_arl', NEW.id_arl, 'id_fondo_pension', NEW.id_fondo_pension), @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_empleado_aupd
AFTER UPDATE ON empleado FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('empleado', 'UPDATE', NEW.codigo_empleado, JSON_OBJECT('codigo_empleado', OLD.codigo_empleado, 'primer_apellido', OLD.primer_apellido, 'segundo_apellido', OLD.segundo_apellido, 'nombres', OLD.nombres, 'fecha_ingreso', OLD.fecha_ingreso, 'salario', OLD.salario, 'id_dependencia', OLD.id_dependencia, 'id_cargo', OLD.id_cargo, 'id_eps', OLD.id_eps, 'id_arl', OLD.id_arl, 'id_fondo_pension', OLD.id_fondo_pension), JSON_OBJECT('codigo_empleado', NEW.codigo_empleado, 'primer_apellido', NEW.primer_apellido, 'segundo_apellido', NEW.segundo_apellido, 'nombres', NEW.nombres, 'fecha_ingreso', NEW.fecha_ingreso, 'salario', NEW.salario, 'id_dependencia', NEW.id_dependencia, 'id_cargo', NEW.id_cargo, 'id_eps', NEW.id_eps, 'id_arl', NEW.id_arl, 'id_fondo_pension', NEW.id_fondo_pension), @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_empleado_adel
AFTER DELETE ON empleado FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('empleado', 'DELETE', OLD.codigo_empleado, JSON_OBJECT('codigo_empleado', OLD.codigo_empleado, 'primer_apellido', OLD.primer_apellido, 'segundo_apellido', OLD.segundo_apellido, 'nombres', OLD.nombres, 'fecha_ingreso', OLD.fecha_ingreso, 'salario', OLD.salario, 'id_dependencia', OLD.id_dependencia, 'id_cargo', OLD.id_cargo, 'id_eps', OLD.id_eps, 'id_arl', OLD.id_arl, 'id_fondo_pension', OLD.id_fondo_pension), NULL, @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_nomina_mensual_ains
AFTER INSERT ON nomina_mensual FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('nomina_mensual', 'INSERT', NEW.id_nomina, NULL, JSON_OBJECT('id_nomina', NEW.id_nomina, 'codigo_empleado', NEW.codigo_empleado, 'id_periodo', NEW.id_periodo, 'dias_trabajados', NEW.dias_trabajados, 'bonificacion', NEW.bonificacion, 'transporte', NEW.transporte), @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_nomina_mensual_aupd
AFTER UPDATE ON nomina_mensual FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('nomina_mensual', 'UPDATE', NEW.id_nomina, JSON_OBJECT('id_nomina', OLD.id_nomina, 'codigo_empleado', OLD.codigo_empleado, 'id_periodo', OLD.id_periodo, 'dias_trabajados', OLD.dias_trabajados, 'bonificacion', OLD.bonificacion, 'transporte', OLD.transporte), JSON_OBJECT('id_nomina', NEW.id_nomina, 'codigo_empleado', NEW.codigo_empleado, 'id_periodo', NEW.id_periodo, 'dias_trabajados', NEW.dias_trabajados, 'bonificacion', NEW.bonificacion, 'transporte', NEW.transporte), @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_nomina_mensual_adel
AFTER DELETE ON nomina_mensual FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('nomina_mensual', 'DELETE', OLD.id_nomina, JSON_OBJECT('id_nomina', OLD.id_nomina, 'codigo_empleado', OLD.codigo_empleado, 'id_periodo', OLD.id_periodo, 'dias_trabajados', OLD.dias_trabajados, 'bonificacion', OLD.bonificacion, 'transporte', OLD.transporte), NULL, @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_novedad_ains
AFTER INSERT ON novedad FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('novedad', 'INSERT', NEW.id_novedad, NULL, JSON_OBJECT('id_novedad', NEW.id_novedad, 'id_nomina', NEW.id_nomina, 'id_tipo_novedad', NEW.id_tipo_novedad, 'fecha_inicio', NEW.fecha_inicio, 'fecha_fin', NEW.fecha_fin, 'dias', NEW.dias), @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_novedad_aupd
AFTER UPDATE ON novedad FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('novedad', 'UPDATE', NEW.id_novedad, JSON_OBJECT('id_novedad', OLD.id_novedad, 'id_nomina', OLD.id_nomina, 'id_tipo_novedad', OLD.id_tipo_novedad, 'fecha_inicio', OLD.fecha_inicio, 'fecha_fin', OLD.fecha_fin, 'dias', OLD.dias), JSON_OBJECT('id_novedad', NEW.id_novedad, 'id_nomina', NEW.id_nomina, 'id_tipo_novedad', NEW.id_tipo_novedad, 'fecha_inicio', NEW.fecha_inicio, 'fecha_fin', NEW.fecha_fin, 'dias', NEW.dias), @app_id_usuario, CURRENT_USER());
  END IF;
END$$
CREATE TRIGGER trg_novedad_adel
AFTER DELETE ON novedad FOR EACH ROW
BEGIN
  IF COALESCE(@auditoria_desactivada, 0) = 0 THEN
    INSERT INTO auditoria_datos (tabla, operacion, id_registro, datos_anteriores, datos_nuevos, id_usuario, usuario_bd)
    VALUES ('novedad', 'DELETE', OLD.id_novedad, JSON_OBJECT('id_novedad', OLD.id_novedad, 'id_nomina', OLD.id_nomina, 'id_tipo_novedad', OLD.id_tipo_novedad, 'fecha_inicio', OLD.fecha_inicio, 'fecha_fin', OLD.fecha_fin, 'dias', OLD.dias), NULL, @app_id_usuario, CURRENT_USER());
  END IF;
END$$
DELIMITER ;

-- =====================================================================
-- 8. VISTAS PARA REPORTES
-- =====================================================================

-- Empleado con todos sus catálogos resueltos (reportes NÓMINA, INFORMACIÓN PERSONAL, SALUD Y PENSIÓN)
CREATE OR REPLACE VIEW v_empleado_detalle AS
SELECT
  e.codigo_empleado,
  CONCAT_WS(' ', e.primer_apellido, e.segundo_apellido, e.nombres) AS nombre_completo,
  e.primer_apellido, e.segundo_apellido, e.nombres,
  d.id_dependencia, d.nombre_dependencia,
  c.id_cargo, c.nombre_cargo,
  e.fecha_ingreso,
  DATE_FORMAT(e.fecha_ingreso, '%d/%m/%Y') AS fecha_ingreso_txt,
  s.id_eps, s.nombre_eps,
  a.id_arl, a.nombre_arl,
  f.id_fondo_pension, f.nombre_fondo,
  e.salario,
  ROUND(e.salario * (SELECT valor FROM parametro_nomina WHERE clave = 'PORC_PENSION_EMPLEADO'), 0)  AS aporte_pension_empleado,
  ROUND(e.salario * (SELECT valor FROM parametro_nomina WHERE clave = 'PORC_PENSION_EMPLEADOR'), 0) AS aporte_pension_empleador
FROM empleado e
JOIN dependencia   d ON d.id_dependencia   = e.id_dependencia
JOIN cargo         c ON c.id_cargo         = e.id_cargo
JOIN eps           s ON s.id_eps           = e.id_eps
JOIN arl           a ON a.id_arl           = e.id_arl
JOIN fondo_pension f ON f.id_fondo_pension = e.id_fondo_pension;

-- Novedades con empleado, dependencia, cargo y periodo (reporte NOVEDADES, filtro MM/AAAA)
CREATE OR REPLACE VIEW v_novedad_detalle AS
SELECT
  n.id_novedad,
  ve.codigo_empleado, ve.nombre_completo,
  ve.id_dependencia, ve.nombre_dependencia,
  ve.id_cargo, ve.nombre_cargo,
  t.nombre_tipo AS tipo_novedad,
  n.fecha_inicio, n.fecha_fin, n.dias,
  p.anio, p.mes,
  CONCAT(LPAD(p.mes, 2, '0'), '/', p.anio) AS periodo_txt,
  STR_TO_DATE(CONCAT(p.anio, '-', p.mes, '-01'), '%Y-%m-%d') AS periodo_fecha
FROM novedad n
JOIN tipo_novedad       t  ON t.id_tipo_novedad  = n.id_tipo_novedad
JOIN nomina_mensual     nm ON nm.id_nomina       = n.id_nomina
JOIN periodo            p  ON p.id_periodo       = nm.id_periodo
JOIN v_empleado_detalle ve ON ve.codigo_empleado = nm.codigo_empleado;

-- Liquidación mensual con conceptos (detalle de nómina por empleado)
CREATE OR REPLACE VIEW v_nomina_detalle AS
SELECT
  nm.id_nomina,
  ve.codigo_empleado, ve.nombre_completo, ve.nombre_dependencia, ve.nombre_cargo,
  p.anio, p.mes,
  CONCAT(LPAD(p.mes, 2, '0'), '/', p.anio) AS periodo_txt,
  ve.salario,
  nm.dias_trabajados,
  ROUND(ve.salario / 30 * nm.dias_trabajados, 0) AS salario_devengado,
  nm.bonificacion,
  nm.transporte,
  (SELECT COUNT(*) FROM novedad n WHERE n.id_nomina = nm.id_nomina) AS cantidad_novedades
FROM nomina_mensual nm
JOIN periodo            p  ON p.id_periodo       = nm.id_periodo
JOIN v_empleado_detalle ve ON ve.codigo_empleado = nm.codigo_empleado;

-- =====================================================================
-- 9. DATOS INICIALES (desde Nomina_normalizada_3FN.xlsx)
-- =====================================================================
SET @auditoria_desactivada = 1;   -- la carga inicial no se registra en auditoria_datos
START TRANSACTION;

INSERT INTO dependencia (id_dependencia, nombre_dependencia) VALUES
  (1, 'Comercial'),
  (2, 'Contabilidad'),
  (3, 'Facturación'),
  (4, 'Tecnología');
INSERT INTO cargo (id_cargo, nombre_cargo) VALUES
  (1, 'Auditor interno'),
  (2, 'Auxiliar especializado'),
  (3, 'DBA'),
  (4, 'Director de cartera'),
  (5, 'Director de costos'),
  (6, 'Director de facturación'),
  (7, 'Director de impuestos'),
  (8, 'Director de presupuestos'),
  (9, 'Director de ventas'),
  (10, 'Gerente de ventas'),
  (11, 'Ingeniero de desarrollo'),
  (12, 'Ingeniero de soporte'),
  (13, 'Líder de infraestructura'),
  (14, 'Líder de QA');
INSERT INTO eps (id_eps, nombre_eps) VALUES
  (1, 'Aliansalud EPS'),
  (2, 'EPS-Sanitas'),
  (3, 'EPS-Sura'),
  (4, 'Nueva EPS');
INSERT INTO arl (id_arl, nombre_arl) VALUES
  (1, 'Positiva');
INSERT INTO fondo_pension (id_fondo_pension, nombre_fondo) VALUES
  (1, 'Colpensiones'),
  (2, 'Porvenir'),
  (3, 'Protección'),
  (4, 'Skandia');
INSERT INTO tipo_novedad (id_tipo_novedad, nombre_tipo) VALUES
  (1, 'INCAPACIDAD'),
  (2, 'VACACIONES');
INSERT INTO periodo (id_periodo, anio, mes) VALUES
  (1, 2022, 3),
  (2, 2022, 4),
  (3, 2022, 5);
-- PENDIENTE CONFIRMAR con el docente cómo se calcula el "Aporte Pensión".
-- Valores de referencia de la ley colombiana (Ley 100 de 1993): 16 % total = 4 % empleado + 12 % empleador.
INSERT INTO parametro_nomina (clave, valor, descripcion) VALUES
  ('PORC_PENSION_EMPLEADO', 0.04, 'Aporte a pensión a cargo del empleado'),
  ('PORC_PENSION_EMPLEADOR', 0.12, 'Aporte a pensión a cargo del empleador'),
  ('PORC_SALUD_EMPLEADO', 0.04, 'Aporte a salud a cargo del empleado');
INSERT INTO empleado (codigo_empleado, primer_apellido, segundo_apellido, nombres, fecha_ingreso, salario, id_dependencia, id_cargo, id_eps, id_arl, id_fondo_pension) VALUES
  (5001, 'AGUDELO', 'ESCOBAR', 'EDWAR DAVID', '2021-03-11', 4395489, 4, 11, 2, 1, 1),
  (5002, 'ALARCON', 'CUBIDES', 'JUAN PABLO', '2020-10-30', 3155500, 3, 2, 1, 1, 3),
  (5003, 'ANDRADE', 'ROJAS', 'MARIO FERNANDO', '2020-08-25', 3582542, 4, 11, 4, 1, 2),
  (5004, 'ARANGO', 'CASTRO', 'RAFAEL ESTEBAN', '2022-02-17', 3512579, 2, 7, 3, 1, 4),
  (5005, 'BARON', 'BECERRA', 'WILLIAM ESTEBAN', '2020-03-11', 4016192, 4, 11, 2, 1, 1),
  (5006, 'BELTRÁN', 'CASTAÑO', 'LOUIS ALEJANDRO', '2020-03-10', 3410252, 1, 10, 1, 1, 4),
  (5007, 'BUITRAGO', 'RIOS', 'JOSE DAVID', '2021-04-11', 3122766, 3, 6, 4, 1, 2),
  (5008, 'CABREJO', 'TRUJILLO', 'JUAN DAVID', '2021-10-24', 3852689, 4, 12, 3, 1, 3),
  (5009, 'CAMARGO', 'SERRANO', 'ISABELLA', '2020-05-21', 2560603, 4, 3, 2, 1, 1),
  (5010, 'CARRASQUILLA', 'BAYTER', 'HENRY SAMUEL', '2020-08-12', 3743655, 2, 1, 1, 1, 4),
  (5011, 'CARVAJAL', 'SANABRIA', 'IVAN DAVID', '2021-08-16', 3538638, 2, 8, 4, 1, 4),
  (5012, 'CASTRO', 'GIRALDO', 'JUAN MANUEL', '2021-03-29', 3124336, 4, 12, 3, 1, 3),
  (5013, 'CASTRO', 'PINILLA', 'JUAN DIEGO', '2021-07-21', 4177447, 4, 13, 3, 1, 1),
  (5014, 'CRUZ', 'BALLESTEROS', 'DAYAN ZELENE', '2021-08-18', 2735729, 2, 1, 2, 1, 2),
  (5015, 'CRUZ', 'MARTINEZ', 'LUIS ESTEBAN', '2020-08-28', 3851336, 4, 13, 1, 1, 3),
  (5016, 'ESCAMILLA', 'BARRERO', 'CRISTIAN CAMILO', '2021-09-25', 4062175, 3, 4, 4, 1, 2),
  (5017, 'GIRALDO', 'BRICEÑO', 'SANTIAGO', '2020-08-24', 3152891, 4, 14, 3, 1, 1),
  (5018, 'GOMEZ', 'GOMEZ', 'CRISTIAN ALBERTO', '2021-09-11', 4487658, 2, 5, 2, 1, 2),
  (5019, 'GONZALEZ', 'BUITRAGO', 'DAVID ORLANDO', '2022-03-26', 4240924, 1, 9, 1, 1, 3),
  (5020, 'LOZANO', 'TOVAR', 'JUAN PABLO', '2021-10-18', 3769836, 1, 9, 2, 1, 2);
INSERT INTO nomina_mensual (id_nomina, codigo_empleado, id_periodo, dias_trabajados, bonificacion, transporte) VALUES
  (1, 5001, 1, 30, 649809, 39764),
  (2, 5002, 1, 30, 328354, 27195),
  (3, 5003, 1, 30, 406552, 36305),
  (4, 5004, 1, 12, 670106, 7475),
  (5, 5005, 1, 30, 228523, 28702),
  (6, 5006, 1, 30, 494233, 1582),
  (7, 5007, 1, 30, 818017, 8004),
  (8, 5008, 1, 20, 569760, 38517),
  (9, 5009, 1, 30, 336775, 14345),
  (10, 5010, 1, 30, 632261, 17441),
  (11, 5011, 1, 30, 157647, 25643),
  (12, 5012, 1, 30, 442282, 24306),
  (13, 5013, 2, 15, 542140, 47866),
  (14, 5014, 1, 30, 890426, 17476),
  (15, 5015, 1, 30, 552774, 36141),
  (16, 5016, 1, 30, 557368, 11870),
  (17, 5017, 3, 25, 37847, 11568),
  (18, 5018, 1, 30, 391789, 44018),
  (19, 5019, 1, 30, 515406, 25063),
  (20, 5020, 1, 30, 94347, 34270);
INSERT INTO novedad (id_novedad, id_nomina, id_tipo_novedad, fecha_inicio, fecha_fin, dias) VALUES
  (1, 4, 1, '2022-03-02', '2022-03-19', 18),
  (2, 8, 2, '2022-03-10', '2022-03-21', 10),
  (3, 13, 2, '2022-04-12', '2022-04-28', 15),
  (4, 17, 1, '2022-05-07', '2022-05-12', 5);
INSERT INTO rol (id_rol, nombre_rol, descripcion) VALUES
  (1, 'ADMINISTRADOR', 'CRUD completo, usuarios, cargas de archivos y auditoría'),
  (2, 'ANALISTA', 'CRUD de nómina y entretenimiento, reportes y cargas de archivos'),
  (3, 'CONSULTA', 'Solo lectura y reportes');
-- Usuario administrador inicial. Contraseña temporal: EntreCol2026*
-- (hash bcrypt, cost 12). La aplicación obliga a cambiarla en el primer ingreso.
INSERT INTO usuario (id_usuario, username, email, nombre_completo, password_hash, id_rol, debe_cambiar_password) VALUES
  (1, 'admin', 'admin@entrecol.local', 'Administrador del sistema', '$2b$12$umUgVERDDcgdzMJJAWaLZOixz1IYWv3y0z9vHjF8aOl/dZgPQjMDq', 1, 1);

COMMIT;
SET @auditoria_desactivada = NULL;

-- =====================================================================
-- 10. USUARIO DE CONEXIÓN DE LA APLICACIÓN (opcional, recomendado)
--     Flask NO debe conectarse como root. Cambie la contraseña antes de usar.
-- =====================================================================
-- CREATE USER IF NOT EXISTS 'entrecol_app'@'localhost' IDENTIFIED BY 'CambieEstaClave_2026';
-- GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE, CREATE TEMPORARY TABLES ON entrecol_db.* TO 'entrecol_app'@'localhost';
-- FLUSH PRIVILEGES;
