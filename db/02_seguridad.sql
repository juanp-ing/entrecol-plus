-- EntreCOL+ - Modulo de seguridad y auditoria
-- Tablas de usuarios, roles y registro de auditoria (RF-01 a RF-04, RF-15 a RF-17)
USE entrecol;

CREATE TABLE rol (
  id_rol       INT          NOT NULL AUTO_INCREMENT,
  nombre_rol   VARCHAR(30)  NOT NULL,
  descripcion  VARCHAR(255) NULL,
  CONSTRAINT pk_rol PRIMARY KEY (id_rol),
  CONSTRAINT uq_rol_nombre UNIQUE (nombre_rol)
) ENGINE = InnoDB;

CREATE TABLE usuario (
  id_usuario      INT           NOT NULL AUTO_INCREMENT,
  nombre_usuario  VARCHAR(50)   NOT NULL,
  nombre_completo VARCHAR(120)  NOT NULL,
  password_hash   CHAR(60)      NOT NULL,           -- hash bcrypt (RF-02)
  id_rol          INT           NOT NULL,
  activo          TINYINT(1)    NOT NULL DEFAULT 1,
  fecha_creacion  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),
  CONSTRAINT uq_usuario_nombre UNIQUE (nombre_usuario),
  CONSTRAINT ck_usuario_activo CHECK (activo IN (0, 1)),
  CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol)
    REFERENCES rol (id_rol) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Cambios de datos, escritos por los triggers (RF-15)
CREATE TABLE auditoria_datos (
  id_auditoria     BIGINT        NOT NULL AUTO_INCREMENT,
  tabla            VARCHAR(64)   NOT NULL,
  operacion        ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  llave            VARCHAR(100)  NOT NULL,
  valores_antes    LONGTEXT      NULL,
  valores_despues  LONGTEXT      NULL,
  usuario_app      VARCHAR(50)   NOT NULL,
  usuario_bd       VARCHAR(100)  NOT NULL,
  fecha            DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_auditoria_datos PRIMARY KEY (id_auditoria),
  CONSTRAINT ck_aud_antes   CHECK (valores_antes IS NULL OR JSON_VALID(valores_antes)),
  CONSTRAINT ck_aud_despues CHECK (valores_despues IS NULL OR JSON_VALID(valores_despues))
) ENGINE = InnoDB;

CREATE INDEX ix_aud_datos_fecha ON auditoria_datos (fecha);
CREATE INDEX ix_aud_datos_tabla ON auditoria_datos (tabla, operacion);

-- Eventos sin cambio de datos, escritos por el middleware de la API (RF-16)
CREATE TABLE auditoria_evento (
  id_evento   BIGINT        NOT NULL AUTO_INCREMENT,
  tipo        ENUM('LOGIN_OK','LOGIN_FALLIDO','LOGOUT','ACCESO','REPORTE','CARGA_ARCHIVO') NOT NULL,
  usuario_app VARCHAR(50)   NOT NULL,
  detalle     VARCHAR(500)  NULL,
  ip          VARCHAR(45)   NULL,
  fecha       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_auditoria_evento PRIMARY KEY (id_evento)
) ENGINE = InnoDB;

CREATE INDEX ix_aud_evento_fecha ON auditoria_evento (fecha);
CREATE INDEX ix_aud_evento_tipo  ON auditoria_evento (tipo, usuario_app);

INSERT INTO rol (nombre_rol, descripcion) VALUES
  ('ADMINISTRADOR', 'Carga archivos, CRUD, usuarios, todos los reportes y auditoria'),
  ('CONSULTA',      'Genera y exporta reportes, sin modificar datos');
