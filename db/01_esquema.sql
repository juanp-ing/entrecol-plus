-- Base de datos EntreCOL+ (MariaDB LTS)
-- Fuente original: entrecol.sql, colacion ajustada a utf8mb4_unicode_ci
CREATE DATABASE IF NOT EXISTS entrecol
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE entrecol;

-- Modulo de nomina

CREATE TABLE dependencia (
  id_dependencia      INT          NOT NULL AUTO_INCREMENT,
  nombre_dependencia  VARCHAR(80)  NOT NULL,
  CONSTRAINT pk_dependencia PRIMARY KEY (id_dependencia),
  CONSTRAINT uq_dependencia_nombre UNIQUE (nombre_dependencia)
) ENGINE = InnoDB;

CREATE TABLE cargo (
  id_cargo      INT          NOT NULL AUTO_INCREMENT,
  nombre_cargo  VARCHAR(80)  NOT NULL,
  CONSTRAINT pk_cargo PRIMARY KEY (id_cargo),
  CONSTRAINT uq_cargo_nombre UNIQUE (nombre_cargo)
) ENGINE = InnoDB;

CREATE TABLE eps (
  id_eps      INT          NOT NULL AUTO_INCREMENT,
  nombre_eps  VARCHAR(80)  NOT NULL,
  CONSTRAINT pk_eps PRIMARY KEY (id_eps),
  CONSTRAINT uq_eps_nombre UNIQUE (nombre_eps)
) ENGINE = InnoDB;

CREATE TABLE arl (
  id_arl      INT          NOT NULL AUTO_INCREMENT,
  nombre_arl  VARCHAR(80)  NOT NULL,
  CONSTRAINT pk_arl PRIMARY KEY (id_arl),
  CONSTRAINT uq_arl_nombre UNIQUE (nombre_arl)
) ENGINE = InnoDB;

CREATE TABLE fondo_pension (
  id_fondo_pension  INT          NOT NULL AUTO_INCREMENT,
  nombre_fondo      VARCHAR(80)  NOT NULL,
  CONSTRAINT pk_fondo_pension PRIMARY KEY (id_fondo_pension),
  CONSTRAINT uq_fondo_pension_nombre UNIQUE (nombre_fondo)
) ENGINE = InnoDB;

CREATE TABLE periodo (
  id_periodo  INT       NOT NULL AUTO_INCREMENT,
  anio        SMALLINT  NOT NULL,
  mes         TINYINT   NOT NULL,
  CONSTRAINT pk_periodo PRIMARY KEY (id_periodo),
  CONSTRAINT uq_periodo_anio_mes UNIQUE (anio, mes),
  CONSTRAINT ck_periodo_mes  CHECK (mes BETWEEN 1 AND 12),
  CONSTRAINT ck_periodo_anio CHECK (anio BETWEEN 1990 AND 2100)
) ENGINE = InnoDB;

CREATE TABLE tipo_novedad (
  id_tipo_novedad  INT          NOT NULL AUTO_INCREMENT,
  nombre_tipo      VARCHAR(40)  NOT NULL,
  CONSTRAINT pk_tipo_novedad PRIMARY KEY (id_tipo_novedad),
  CONSTRAINT uq_tipo_novedad_nombre UNIQUE (nombre_tipo)
) ENGINE = InnoDB;

CREATE TABLE parametro_nomina (
  id_parametro  INT            NOT NULL AUTO_INCREMENT,
  clave         VARCHAR(50)    NOT NULL,
  valor         DECIMAL(14,4)  NOT NULL,
  descripcion   VARCHAR(255)   NULL,
  CONSTRAINT pk_parametro_nomina PRIMARY KEY (id_parametro),
  CONSTRAINT uq_parametro_clave UNIQUE (clave)
) ENGINE = InnoDB;

-- Tabla de empleados
CREATE TABLE empleado (
  codigo_empleado   INT            NOT NULL,
  primer_apellido   VARCHAR(50)    NOT NULL,
  segundo_apellido  VARCHAR(50)    NULL,
  nombres           VARCHAR(80)    NOT NULL,
  fecha_ingreso     DATE           NOT NULL,
  salario           DECIMAL(12,2)  NOT NULL,
  id_dependencia    INT            NOT NULL,
  id_cargo          INT            NOT NULL,
  id_eps            INT            NOT NULL,
  id_arl            INT            NOT NULL,
  id_fondo_pension  INT            NOT NULL,
  CONSTRAINT pk_empleado PRIMARY KEY (codigo_empleado),
  CONSTRAINT ck_empleado_salario CHECK (salario > 0),
  CONSTRAINT fk_empleado_dependencia FOREIGN KEY (id_dependencia)
    REFERENCES dependencia (id_dependencia) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_cargo FOREIGN KEY (id_cargo)
    REFERENCES cargo (id_cargo) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_eps FOREIGN KEY (id_eps)
    REFERENCES eps (id_eps) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_arl FOREIGN KEY (id_arl)
    REFERENCES arl (id_arl) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_empleado_fondo FOREIGN KEY (id_fondo_pension)
    REFERENCES fondo_pension (id_fondo_pension) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Liquidacion mensual
CREATE TABLE nomina_mensual (
  id_nomina        INT            NOT NULL AUTO_INCREMENT,
  codigo_empleado  INT            NOT NULL,
  id_periodo       INT            NOT NULL,
  dias_trabajados  TINYINT        NOT NULL,
  bonificacion     DECIMAL(12,2)  NOT NULL DEFAULT 0,
  transporte       DECIMAL(12,2)  NOT NULL DEFAULT 0,
  CONSTRAINT pk_nomina_mensual PRIMARY KEY (id_nomina),
  CONSTRAINT uq_nomina_empleado_periodo UNIQUE (codigo_empleado, id_periodo),
  CONSTRAINT ck_nomina_dias CHECK (dias_trabajados BETWEEN 0 AND 30),
  CONSTRAINT ck_nomina_bonificacion CHECK (bonificacion >= 0),
  CONSTRAINT ck_nomina_transporte CHECK (transporte >= 0),
  CONSTRAINT fk_nomina_empleado FOREIGN KEY (codigo_empleado)
    REFERENCES empleado (codigo_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_nomina_periodo FOREIGN KEY (id_periodo)
    REFERENCES periodo (id_periodo) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Novedades de nomina
CREATE TABLE novedad (
  id_novedad       INT      NOT NULL AUTO_INCREMENT,
  id_nomina        INT      NOT NULL,
  id_tipo_novedad  INT      NOT NULL,
  fecha_inicio     DATE     NOT NULL,
  fecha_fin        DATE     NOT NULL,
  dias             TINYINT  NOT NULL,
  CONSTRAINT pk_novedad PRIMARY KEY (id_novedad),
  CONSTRAINT ck_novedad_fechas CHECK (fecha_fin >= fecha_inicio),
  CONSTRAINT ck_novedad_dias CHECK (dias BETWEEN 1 AND 31),
  CONSTRAINT fk_novedad_nomina FOREIGN KEY (id_nomina)
    REFERENCES nomina_mensual (id_nomina) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_novedad_tipo FOREIGN KEY (id_tipo_novedad)
    REFERENCES tipo_novedad (id_tipo_novedad) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE INDEX ix_empleado_apellidos ON empleado (primer_apellido, segundo_apellido, nombres);
CREATE INDEX ix_novedad_fechas     ON novedad (fecha_inicio, fecha_fin);

-- Datos iniciales
INSERT INTO tipo_novedad (nombre_tipo) VALUES
  ('INCAPACIDAD'),
  ('VACACIONES');

INSERT INTO parametro_nomina (clave, valor, descripcion) VALUES
  ('PORC_APORTE_PENSION_EMPLEADO', 0.0400,
   'Porcentaje de aporte a pension');


-- Modulo de entretenimiento

-- Peliculas
CREATE TABLE pelicula (
  id_pelicula  INT           NOT NULL,
  titulo       VARCHAR(255)  NOT NULL,
  anio         SMALLINT      NOT NULL,
  CONSTRAINT pk_pelicula PRIMARY KEY (id_pelicula),
  CONSTRAINT ck_pelicula_anio CHECK (anio BETWEEN 1880 AND 2100)
) ENGINE = InnoDB;

CREATE TABLE genero (
  id_genero      INT          NOT NULL AUTO_INCREMENT,
  nombre_genero  VARCHAR(40)  NOT NULL,
  CONSTRAINT pk_genero PRIMARY KEY (id_genero),
  CONSTRAINT uq_genero_nombre UNIQUE (nombre_genero)
) ENGINE = InnoDB;

CREATE TABLE pelicula_genero (
  id_pelicula  INT  NOT NULL,
  id_genero    INT  NOT NULL,
  CONSTRAINT pk_pelicula_genero PRIMARY KEY (id_pelicula, id_genero),
  CONSTRAINT fk_pg_pelicula FOREIGN KEY (id_pelicula)
    REFERENCES pelicula (id_pelicula) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_pg_genero FOREIGN KEY (id_genero)
    REFERENCES genero (id_genero) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE INDEX ix_pelicula_anio   ON pelicula (anio);
CREATE INDEX ix_pg_genero       ON pelicula_genero (id_genero);

-- Libros
CREATE TABLE editorial (
  id_editorial      INT           NOT NULL AUTO_INCREMENT,
  nombre_editorial  VARCHAR(150)  NOT NULL,
  CONSTRAINT pk_editorial PRIMARY KEY (id_editorial),
  CONSTRAINT uq_editorial_nombre UNIQUE (nombre_editorial)
) ENGINE = InnoDB;

CREATE TABLE idioma (
  id_idioma      INT          NOT NULL AUTO_INCREMENT,
  codigo_idioma  VARCHAR(10)  NOT NULL,
  CONSTRAINT pk_idioma PRIMARY KEY (id_idioma),
  CONSTRAINT uq_idioma_codigo UNIQUE (codigo_idioma)
) ENGINE = InnoDB;

CREATE TABLE autor (
  id_autor      INT           NOT NULL AUTO_INCREMENT,
  nombre_autor  VARCHAR(150)  NOT NULL,
  CONSTRAINT pk_autor PRIMARY KEY (id_autor),
  CONSTRAINT uq_autor_nombre UNIQUE (nombre_autor)
) ENGINE = InnoDB;

CREATE TABLE serie (
  id_serie      INT           NOT NULL AUTO_INCREMENT,
  nombre_serie  VARCHAR(150)  NOT NULL,
  CONSTRAINT pk_serie PRIMARY KEY (id_serie),
  CONSTRAINT uq_serie_nombre UNIQUE (nombre_serie)
) ENGINE = InnoDB;

CREATE TABLE libro (
  id_libro           INT           NOT NULL,
  titulo             VARCHAR(255)  NOT NULL,
  isbn               VARCHAR(10)   NULL,
  isbn13             CHAR(13)      NULL,
  num_paginas        INT           NULL,
  fecha_publicacion  DATE          NULL,
  rating_promedio    DECIMAL(3,2)  NULL,
  cantidad_ratings   INT           NOT NULL DEFAULT 0,
  cantidad_resenas   INT           NOT NULL DEFAULT 0,
  id_editorial       INT           NOT NULL,
  id_idioma          INT           NOT NULL,
  CONSTRAINT pk_libro PRIMARY KEY (id_libro),
  CONSTRAINT uq_libro_isbn   UNIQUE (isbn),
  CONSTRAINT uq_libro_isbn13 UNIQUE (isbn13),
  CONSTRAINT ck_libro_rating   CHECK (rating_promedio BETWEEN 0 AND 5),
  CONSTRAINT ck_libro_paginas  CHECK (num_paginas >= 0),
  CONSTRAINT ck_libro_ratings  CHECK (cantidad_ratings >= 0),
  CONSTRAINT ck_libro_resenas  CHECK (cantidad_resenas >= 0),
  CONSTRAINT fk_libro_editorial FOREIGN KEY (id_editorial)
    REFERENCES editorial (id_editorial) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_libro_idioma FOREIGN KEY (id_idioma)
    REFERENCES idioma (id_idioma) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE libro_autor (
  id_libro  INT      NOT NULL,
  id_autor  INT      NOT NULL,
  orden     TINYINT  NOT NULL,
  CONSTRAINT pk_libro_autor PRIMARY KEY (id_libro, id_autor),
  CONSTRAINT ck_libro_autor_orden CHECK (orden >= 1),
  CONSTRAINT fk_la_libro FOREIGN KEY (id_libro)
    REFERENCES libro (id_libro) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_la_autor FOREIGN KEY (id_autor)
    REFERENCES autor (id_autor) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE libro_serie (
  id_libro         INT          NOT NULL,
  id_serie         INT          NOT NULL,
  numero_en_serie  VARCHAR(20)  NULL,
  CONSTRAINT pk_libro_serie PRIMARY KEY (id_libro, id_serie),
  CONSTRAINT fk_ls_libro FOREIGN KEY (id_libro)
    REFERENCES libro (id_libro) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ls_serie FOREIGN KEY (id_serie)
    REFERENCES serie (id_serie) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE INDEX ix_libro_rating ON libro (rating_promedio);
CREATE INDEX ix_libro_fecha  ON libro (fecha_publicacion);
CREATE INDEX ix_la_autor     ON libro_autor (id_autor);
CREATE INDEX ix_ls_serie     ON libro_serie (id_serie);
