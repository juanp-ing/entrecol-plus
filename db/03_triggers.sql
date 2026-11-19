-- EntreCOL+ - Triggers de auditoria (GENERADO por scripts/generar_triggers.py, no editar a mano)
USE entrecol;
DELIMITER $$

DROP TRIGGER IF EXISTS trg_dependencia_ai$$
CREATE TRIGGER trg_dependencia_ai AFTER INSERT ON dependencia
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('dependencia', 'INSERT', CAST(NEW.id_dependencia AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_dependencia', NEW.id_dependencia,
      'nombre_dependencia', NEW.nombre_dependencia),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_dependencia_au$$
CREATE TRIGGER trg_dependencia_au AFTER UPDATE ON dependencia
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_dependencia <=> NEW.id_dependencia AND OLD.nombre_dependencia <=> NEW.nombre_dependencia) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('dependencia', 'UPDATE', CAST(NEW.id_dependencia AS CHAR),
    JSON_OBJECT(
      'id_dependencia', OLD.id_dependencia,
      'nombre_dependencia', OLD.nombre_dependencia),
    JSON_OBJECT(
      'id_dependencia', NEW.id_dependencia,
      'nombre_dependencia', NEW.nombre_dependencia),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_dependencia_ad$$
CREATE TRIGGER trg_dependencia_ad AFTER DELETE ON dependencia
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('dependencia', 'DELETE', CAST(OLD.id_dependencia AS CHAR),
    JSON_OBJECT(
      'id_dependencia', OLD.id_dependencia,
      'nombre_dependencia', OLD.nombre_dependencia),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_cargo_ai$$
CREATE TRIGGER trg_cargo_ai AFTER INSERT ON cargo
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('cargo', 'INSERT', CAST(NEW.id_cargo AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_cargo', NEW.id_cargo,
      'nombre_cargo', NEW.nombre_cargo),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_cargo_au$$
CREATE TRIGGER trg_cargo_au AFTER UPDATE ON cargo
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_cargo <=> NEW.id_cargo AND OLD.nombre_cargo <=> NEW.nombre_cargo) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('cargo', 'UPDATE', CAST(NEW.id_cargo AS CHAR),
    JSON_OBJECT(
      'id_cargo', OLD.id_cargo,
      'nombre_cargo', OLD.nombre_cargo),
    JSON_OBJECT(
      'id_cargo', NEW.id_cargo,
      'nombre_cargo', NEW.nombre_cargo),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_cargo_ad$$
CREATE TRIGGER trg_cargo_ad AFTER DELETE ON cargo
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('cargo', 'DELETE', CAST(OLD.id_cargo AS CHAR),
    JSON_OBJECT(
      'id_cargo', OLD.id_cargo,
      'nombre_cargo', OLD.nombre_cargo),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_eps_ai$$
CREATE TRIGGER trg_eps_ai AFTER INSERT ON eps
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('eps', 'INSERT', CAST(NEW.id_eps AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_eps', NEW.id_eps,
      'nombre_eps', NEW.nombre_eps),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_eps_au$$
CREATE TRIGGER trg_eps_au AFTER UPDATE ON eps
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_eps <=> NEW.id_eps AND OLD.nombre_eps <=> NEW.nombre_eps) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('eps', 'UPDATE', CAST(NEW.id_eps AS CHAR),
    JSON_OBJECT(
      'id_eps', OLD.id_eps,
      'nombre_eps', OLD.nombre_eps),
    JSON_OBJECT(
      'id_eps', NEW.id_eps,
      'nombre_eps', NEW.nombre_eps),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_eps_ad$$
CREATE TRIGGER trg_eps_ad AFTER DELETE ON eps
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('eps', 'DELETE', CAST(OLD.id_eps AS CHAR),
    JSON_OBJECT(
      'id_eps', OLD.id_eps,
      'nombre_eps', OLD.nombre_eps),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_arl_ai$$
CREATE TRIGGER trg_arl_ai AFTER INSERT ON arl
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('arl', 'INSERT', CAST(NEW.id_arl AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_arl', NEW.id_arl,
      'nombre_arl', NEW.nombre_arl),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_arl_au$$
CREATE TRIGGER trg_arl_au AFTER UPDATE ON arl
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_arl <=> NEW.id_arl AND OLD.nombre_arl <=> NEW.nombre_arl) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('arl', 'UPDATE', CAST(NEW.id_arl AS CHAR),
    JSON_OBJECT(
      'id_arl', OLD.id_arl,
      'nombre_arl', OLD.nombre_arl),
    JSON_OBJECT(
      'id_arl', NEW.id_arl,
      'nombre_arl', NEW.nombre_arl),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_arl_ad$$
CREATE TRIGGER trg_arl_ad AFTER DELETE ON arl
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('arl', 'DELETE', CAST(OLD.id_arl AS CHAR),
    JSON_OBJECT(
      'id_arl', OLD.id_arl,
      'nombre_arl', OLD.nombre_arl),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_fondo_pension_ai$$
CREATE TRIGGER trg_fondo_pension_ai AFTER INSERT ON fondo_pension
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('fondo_pension', 'INSERT', CAST(NEW.id_fondo_pension AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_fondo_pension', NEW.id_fondo_pension,
      'nombre_fondo', NEW.nombre_fondo),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_fondo_pension_au$$
CREATE TRIGGER trg_fondo_pension_au AFTER UPDATE ON fondo_pension
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_fondo_pension <=> NEW.id_fondo_pension AND OLD.nombre_fondo <=> NEW.nombre_fondo) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('fondo_pension', 'UPDATE', CAST(NEW.id_fondo_pension AS CHAR),
    JSON_OBJECT(
      'id_fondo_pension', OLD.id_fondo_pension,
      'nombre_fondo', OLD.nombre_fondo),
    JSON_OBJECT(
      'id_fondo_pension', NEW.id_fondo_pension,
      'nombre_fondo', NEW.nombre_fondo),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_fondo_pension_ad$$
CREATE TRIGGER trg_fondo_pension_ad AFTER DELETE ON fondo_pension
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('fondo_pension', 'DELETE', CAST(OLD.id_fondo_pension AS CHAR),
    JSON_OBJECT(
      'id_fondo_pension', OLD.id_fondo_pension,
      'nombre_fondo', OLD.nombre_fondo),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_periodo_ai$$
CREATE TRIGGER trg_periodo_ai AFTER INSERT ON periodo
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('periodo', 'INSERT', CAST(NEW.id_periodo AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_periodo', NEW.id_periodo,
      'anio', NEW.anio,
      'mes', NEW.mes),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_periodo_au$$
CREATE TRIGGER trg_periodo_au AFTER UPDATE ON periodo
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_periodo <=> NEW.id_periodo AND OLD.anio <=> NEW.anio AND OLD.mes <=> NEW.mes) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('periodo', 'UPDATE', CAST(NEW.id_periodo AS CHAR),
    JSON_OBJECT(
      'id_periodo', OLD.id_periodo,
      'anio', OLD.anio,
      'mes', OLD.mes),
    JSON_OBJECT(
      'id_periodo', NEW.id_periodo,
      'anio', NEW.anio,
      'mes', NEW.mes),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_periodo_ad$$
CREATE TRIGGER trg_periodo_ad AFTER DELETE ON periodo
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('periodo', 'DELETE', CAST(OLD.id_periodo AS CHAR),
    JSON_OBJECT(
      'id_periodo', OLD.id_periodo,
      'anio', OLD.anio,
      'mes', OLD.mes),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_tipo_novedad_ai$$
CREATE TRIGGER trg_tipo_novedad_ai AFTER INSERT ON tipo_novedad
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('tipo_novedad', 'INSERT', CAST(NEW.id_tipo_novedad AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_tipo_novedad', NEW.id_tipo_novedad,
      'nombre_tipo', NEW.nombre_tipo),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_tipo_novedad_au$$
CREATE TRIGGER trg_tipo_novedad_au AFTER UPDATE ON tipo_novedad
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_tipo_novedad <=> NEW.id_tipo_novedad AND OLD.nombre_tipo <=> NEW.nombre_tipo) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('tipo_novedad', 'UPDATE', CAST(NEW.id_tipo_novedad AS CHAR),
    JSON_OBJECT(
      'id_tipo_novedad', OLD.id_tipo_novedad,
      'nombre_tipo', OLD.nombre_tipo),
    JSON_OBJECT(
      'id_tipo_novedad', NEW.id_tipo_novedad,
      'nombre_tipo', NEW.nombre_tipo),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_tipo_novedad_ad$$
CREATE TRIGGER trg_tipo_novedad_ad AFTER DELETE ON tipo_novedad
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('tipo_novedad', 'DELETE', CAST(OLD.id_tipo_novedad AS CHAR),
    JSON_OBJECT(
      'id_tipo_novedad', OLD.id_tipo_novedad,
      'nombre_tipo', OLD.nombre_tipo),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_parametro_nomina_ai$$
CREATE TRIGGER trg_parametro_nomina_ai AFTER INSERT ON parametro_nomina
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('parametro_nomina', 'INSERT', CAST(NEW.id_parametro AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_parametro', NEW.id_parametro,
      'clave', NEW.clave,
      'valor', NEW.valor,
      'descripcion', NEW.descripcion),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_parametro_nomina_au$$
CREATE TRIGGER trg_parametro_nomina_au AFTER UPDATE ON parametro_nomina
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_parametro <=> NEW.id_parametro AND OLD.clave <=> NEW.clave AND OLD.valor <=> NEW.valor AND OLD.descripcion <=> NEW.descripcion) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('parametro_nomina', 'UPDATE', CAST(NEW.id_parametro AS CHAR),
    JSON_OBJECT(
      'id_parametro', OLD.id_parametro,
      'clave', OLD.clave,
      'valor', OLD.valor,
      'descripcion', OLD.descripcion),
    JSON_OBJECT(
      'id_parametro', NEW.id_parametro,
      'clave', NEW.clave,
      'valor', NEW.valor,
      'descripcion', NEW.descripcion),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_parametro_nomina_ad$$
CREATE TRIGGER trg_parametro_nomina_ad AFTER DELETE ON parametro_nomina
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('parametro_nomina', 'DELETE', CAST(OLD.id_parametro AS CHAR),
    JSON_OBJECT(
      'id_parametro', OLD.id_parametro,
      'clave', OLD.clave,
      'valor', OLD.valor,
      'descripcion', OLD.descripcion),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_empleado_ai$$
CREATE TRIGGER trg_empleado_ai AFTER INSERT ON empleado
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('empleado', 'INSERT', CAST(NEW.codigo_empleado AS CHAR),
    NULL,
    JSON_OBJECT(
      'codigo_empleado', NEW.codigo_empleado,
      'primer_apellido', NEW.primer_apellido,
      'segundo_apellido', NEW.segundo_apellido,
      'nombres', NEW.nombres,
      'fecha_ingreso', NEW.fecha_ingreso,
      'salario', NEW.salario,
      'id_dependencia', NEW.id_dependencia,
      'id_cargo', NEW.id_cargo,
      'id_eps', NEW.id_eps,
      'id_arl', NEW.id_arl,
      'id_fondo_pension', NEW.id_fondo_pension),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_empleado_au$$
CREATE TRIGGER trg_empleado_au AFTER UPDATE ON empleado
FOR EACH ROW
BEGIN
  IF NOT (OLD.codigo_empleado <=> NEW.codigo_empleado AND OLD.primer_apellido <=> NEW.primer_apellido AND OLD.segundo_apellido <=> NEW.segundo_apellido AND OLD.nombres <=> NEW.nombres AND OLD.fecha_ingreso <=> NEW.fecha_ingreso AND OLD.salario <=> NEW.salario AND OLD.id_dependencia <=> NEW.id_dependencia AND OLD.id_cargo <=> NEW.id_cargo AND OLD.id_eps <=> NEW.id_eps AND OLD.id_arl <=> NEW.id_arl AND OLD.id_fondo_pension <=> NEW.id_fondo_pension) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('empleado', 'UPDATE', CAST(NEW.codigo_empleado AS CHAR),
    JSON_OBJECT(
      'codigo_empleado', OLD.codigo_empleado,
      'primer_apellido', OLD.primer_apellido,
      'segundo_apellido', OLD.segundo_apellido,
      'nombres', OLD.nombres,
      'fecha_ingreso', OLD.fecha_ingreso,
      'salario', OLD.salario,
      'id_dependencia', OLD.id_dependencia,
      'id_cargo', OLD.id_cargo,
      'id_eps', OLD.id_eps,
      'id_arl', OLD.id_arl,
      'id_fondo_pension', OLD.id_fondo_pension),
    JSON_OBJECT(
      'codigo_empleado', NEW.codigo_empleado,
      'primer_apellido', NEW.primer_apellido,
      'segundo_apellido', NEW.segundo_apellido,
      'nombres', NEW.nombres,
      'fecha_ingreso', NEW.fecha_ingreso,
      'salario', NEW.salario,
      'id_dependencia', NEW.id_dependencia,
      'id_cargo', NEW.id_cargo,
      'id_eps', NEW.id_eps,
      'id_arl', NEW.id_arl,
      'id_fondo_pension', NEW.id_fondo_pension),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_empleado_ad$$
CREATE TRIGGER trg_empleado_ad AFTER DELETE ON empleado
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('empleado', 'DELETE', CAST(OLD.codigo_empleado AS CHAR),
    JSON_OBJECT(
      'codigo_empleado', OLD.codigo_empleado,
      'primer_apellido', OLD.primer_apellido,
      'segundo_apellido', OLD.segundo_apellido,
      'nombres', OLD.nombres,
      'fecha_ingreso', OLD.fecha_ingreso,
      'salario', OLD.salario,
      'id_dependencia', OLD.id_dependencia,
      'id_cargo', OLD.id_cargo,
      'id_eps', OLD.id_eps,
      'id_arl', OLD.id_arl,
      'id_fondo_pension', OLD.id_fondo_pension),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_nomina_mensual_ai$$
CREATE TRIGGER trg_nomina_mensual_ai AFTER INSERT ON nomina_mensual
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('nomina_mensual', 'INSERT', CAST(NEW.id_nomina AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_nomina', NEW.id_nomina,
      'codigo_empleado', NEW.codigo_empleado,
      'id_periodo', NEW.id_periodo,
      'dias_trabajados', NEW.dias_trabajados,
      'bonificacion', NEW.bonificacion,
      'transporte', NEW.transporte),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_nomina_mensual_au$$
CREATE TRIGGER trg_nomina_mensual_au AFTER UPDATE ON nomina_mensual
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_nomina <=> NEW.id_nomina AND OLD.codigo_empleado <=> NEW.codigo_empleado AND OLD.id_periodo <=> NEW.id_periodo AND OLD.dias_trabajados <=> NEW.dias_trabajados AND OLD.bonificacion <=> NEW.bonificacion AND OLD.transporte <=> NEW.transporte) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('nomina_mensual', 'UPDATE', CAST(NEW.id_nomina AS CHAR),
    JSON_OBJECT(
      'id_nomina', OLD.id_nomina,
      'codigo_empleado', OLD.codigo_empleado,
      'id_periodo', OLD.id_periodo,
      'dias_trabajados', OLD.dias_trabajados,
      'bonificacion', OLD.bonificacion,
      'transporte', OLD.transporte),
    JSON_OBJECT(
      'id_nomina', NEW.id_nomina,
      'codigo_empleado', NEW.codigo_empleado,
      'id_periodo', NEW.id_periodo,
      'dias_trabajados', NEW.dias_trabajados,
      'bonificacion', NEW.bonificacion,
      'transporte', NEW.transporte),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_nomina_mensual_ad$$
CREATE TRIGGER trg_nomina_mensual_ad AFTER DELETE ON nomina_mensual
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('nomina_mensual', 'DELETE', CAST(OLD.id_nomina AS CHAR),
    JSON_OBJECT(
      'id_nomina', OLD.id_nomina,
      'codigo_empleado', OLD.codigo_empleado,
      'id_periodo', OLD.id_periodo,
      'dias_trabajados', OLD.dias_trabajados,
      'bonificacion', OLD.bonificacion,
      'transporte', OLD.transporte),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_novedad_ai$$
CREATE TRIGGER trg_novedad_ai AFTER INSERT ON novedad
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('novedad', 'INSERT', CAST(NEW.id_novedad AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_novedad', NEW.id_novedad,
      'id_nomina', NEW.id_nomina,
      'id_tipo_novedad', NEW.id_tipo_novedad,
      'fecha_inicio', NEW.fecha_inicio,
      'fecha_fin', NEW.fecha_fin,
      'dias', NEW.dias),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_novedad_au$$
CREATE TRIGGER trg_novedad_au AFTER UPDATE ON novedad
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_novedad <=> NEW.id_novedad AND OLD.id_nomina <=> NEW.id_nomina AND OLD.id_tipo_novedad <=> NEW.id_tipo_novedad AND OLD.fecha_inicio <=> NEW.fecha_inicio AND OLD.fecha_fin <=> NEW.fecha_fin AND OLD.dias <=> NEW.dias) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('novedad', 'UPDATE', CAST(NEW.id_novedad AS CHAR),
    JSON_OBJECT(
      'id_novedad', OLD.id_novedad,
      'id_nomina', OLD.id_nomina,
      'id_tipo_novedad', OLD.id_tipo_novedad,
      'fecha_inicio', OLD.fecha_inicio,
      'fecha_fin', OLD.fecha_fin,
      'dias', OLD.dias),
    JSON_OBJECT(
      'id_novedad', NEW.id_novedad,
      'id_nomina', NEW.id_nomina,
      'id_tipo_novedad', NEW.id_tipo_novedad,
      'fecha_inicio', NEW.fecha_inicio,
      'fecha_fin', NEW.fecha_fin,
      'dias', NEW.dias),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_novedad_ad$$
CREATE TRIGGER trg_novedad_ad AFTER DELETE ON novedad
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('novedad', 'DELETE', CAST(OLD.id_novedad AS CHAR),
    JSON_OBJECT(
      'id_novedad', OLD.id_novedad,
      'id_nomina', OLD.id_nomina,
      'id_tipo_novedad', OLD.id_tipo_novedad,
      'fecha_inicio', OLD.fecha_inicio,
      'fecha_fin', OLD.fecha_fin,
      'dias', OLD.dias),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_pelicula_ai$$
CREATE TRIGGER trg_pelicula_ai AFTER INSERT ON pelicula
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('pelicula', 'INSERT', CAST(NEW.id_pelicula AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_pelicula', NEW.id_pelicula,
      'titulo', NEW.titulo,
      'anio', NEW.anio),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_pelicula_au$$
CREATE TRIGGER trg_pelicula_au AFTER UPDATE ON pelicula
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_pelicula <=> NEW.id_pelicula AND OLD.titulo <=> NEW.titulo AND OLD.anio <=> NEW.anio) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('pelicula', 'UPDATE', CAST(NEW.id_pelicula AS CHAR),
    JSON_OBJECT(
      'id_pelicula', OLD.id_pelicula,
      'titulo', OLD.titulo,
      'anio', OLD.anio),
    JSON_OBJECT(
      'id_pelicula', NEW.id_pelicula,
      'titulo', NEW.titulo,
      'anio', NEW.anio),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_pelicula_ad$$
CREATE TRIGGER trg_pelicula_ad AFTER DELETE ON pelicula
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('pelicula', 'DELETE', CAST(OLD.id_pelicula AS CHAR),
    JSON_OBJECT(
      'id_pelicula', OLD.id_pelicula,
      'titulo', OLD.titulo,
      'anio', OLD.anio),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_genero_ai$$
CREATE TRIGGER trg_genero_ai AFTER INSERT ON genero
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('genero', 'INSERT', CAST(NEW.id_genero AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_genero', NEW.id_genero,
      'nombre_genero', NEW.nombre_genero),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_genero_au$$
CREATE TRIGGER trg_genero_au AFTER UPDATE ON genero
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_genero <=> NEW.id_genero AND OLD.nombre_genero <=> NEW.nombre_genero) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('genero', 'UPDATE', CAST(NEW.id_genero AS CHAR),
    JSON_OBJECT(
      'id_genero', OLD.id_genero,
      'nombre_genero', OLD.nombre_genero),
    JSON_OBJECT(
      'id_genero', NEW.id_genero,
      'nombre_genero', NEW.nombre_genero),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_genero_ad$$
CREATE TRIGGER trg_genero_ad AFTER DELETE ON genero
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('genero', 'DELETE', CAST(OLD.id_genero AS CHAR),
    JSON_OBJECT(
      'id_genero', OLD.id_genero,
      'nombre_genero', OLD.nombre_genero),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_pelicula_genero_ai$$
CREATE TRIGGER trg_pelicula_genero_ai AFTER INSERT ON pelicula_genero
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('pelicula_genero', 'INSERT', CONCAT_WS('|', NEW.id_pelicula, NEW.id_genero),
    NULL,
    JSON_OBJECT(
      'id_pelicula', NEW.id_pelicula,
      'id_genero', NEW.id_genero),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_pelicula_genero_au$$
CREATE TRIGGER trg_pelicula_genero_au AFTER UPDATE ON pelicula_genero
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_pelicula <=> NEW.id_pelicula AND OLD.id_genero <=> NEW.id_genero) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('pelicula_genero', 'UPDATE', CONCAT_WS('|', NEW.id_pelicula, NEW.id_genero),
    JSON_OBJECT(
      'id_pelicula', OLD.id_pelicula,
      'id_genero', OLD.id_genero),
    JSON_OBJECT(
      'id_pelicula', NEW.id_pelicula,
      'id_genero', NEW.id_genero),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_pelicula_genero_ad$$
CREATE TRIGGER trg_pelicula_genero_ad AFTER DELETE ON pelicula_genero
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('pelicula_genero', 'DELETE', CONCAT_WS('|', OLD.id_pelicula, OLD.id_genero),
    JSON_OBJECT(
      'id_pelicula', OLD.id_pelicula,
      'id_genero', OLD.id_genero),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_editorial_ai$$
CREATE TRIGGER trg_editorial_ai AFTER INSERT ON editorial
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('editorial', 'INSERT', CAST(NEW.id_editorial AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_editorial', NEW.id_editorial,
      'nombre_editorial', NEW.nombre_editorial),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_editorial_au$$
CREATE TRIGGER trg_editorial_au AFTER UPDATE ON editorial
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_editorial <=> NEW.id_editorial AND OLD.nombre_editorial <=> NEW.nombre_editorial) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('editorial', 'UPDATE', CAST(NEW.id_editorial AS CHAR),
    JSON_OBJECT(
      'id_editorial', OLD.id_editorial,
      'nombre_editorial', OLD.nombre_editorial),
    JSON_OBJECT(
      'id_editorial', NEW.id_editorial,
      'nombre_editorial', NEW.nombre_editorial),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_editorial_ad$$
CREATE TRIGGER trg_editorial_ad AFTER DELETE ON editorial
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('editorial', 'DELETE', CAST(OLD.id_editorial AS CHAR),
    JSON_OBJECT(
      'id_editorial', OLD.id_editorial,
      'nombre_editorial', OLD.nombre_editorial),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_idioma_ai$$
CREATE TRIGGER trg_idioma_ai AFTER INSERT ON idioma
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('idioma', 'INSERT', CAST(NEW.id_idioma AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_idioma', NEW.id_idioma,
      'codigo_idioma', NEW.codigo_idioma),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_idioma_au$$
CREATE TRIGGER trg_idioma_au AFTER UPDATE ON idioma
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_idioma <=> NEW.id_idioma AND OLD.codigo_idioma <=> NEW.codigo_idioma) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('idioma', 'UPDATE', CAST(NEW.id_idioma AS CHAR),
    JSON_OBJECT(
      'id_idioma', OLD.id_idioma,
      'codigo_idioma', OLD.codigo_idioma),
    JSON_OBJECT(
      'id_idioma', NEW.id_idioma,
      'codigo_idioma', NEW.codigo_idioma),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_idioma_ad$$
CREATE TRIGGER trg_idioma_ad AFTER DELETE ON idioma
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('idioma', 'DELETE', CAST(OLD.id_idioma AS CHAR),
    JSON_OBJECT(
      'id_idioma', OLD.id_idioma,
      'codigo_idioma', OLD.codigo_idioma),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_autor_ai$$
CREATE TRIGGER trg_autor_ai AFTER INSERT ON autor
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('autor', 'INSERT', CAST(NEW.id_autor AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_autor', NEW.id_autor,
      'nombre_autor', NEW.nombre_autor),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_autor_au$$
CREATE TRIGGER trg_autor_au AFTER UPDATE ON autor
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_autor <=> NEW.id_autor AND OLD.nombre_autor <=> NEW.nombre_autor) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('autor', 'UPDATE', CAST(NEW.id_autor AS CHAR),
    JSON_OBJECT(
      'id_autor', OLD.id_autor,
      'nombre_autor', OLD.nombre_autor),
    JSON_OBJECT(
      'id_autor', NEW.id_autor,
      'nombre_autor', NEW.nombre_autor),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_autor_ad$$
CREATE TRIGGER trg_autor_ad AFTER DELETE ON autor
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('autor', 'DELETE', CAST(OLD.id_autor AS CHAR),
    JSON_OBJECT(
      'id_autor', OLD.id_autor,
      'nombre_autor', OLD.nombre_autor),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_serie_ai$$
CREATE TRIGGER trg_serie_ai AFTER INSERT ON serie
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('serie', 'INSERT', CAST(NEW.id_serie AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_serie', NEW.id_serie,
      'nombre_serie', NEW.nombre_serie),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_serie_au$$
CREATE TRIGGER trg_serie_au AFTER UPDATE ON serie
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_serie <=> NEW.id_serie AND OLD.nombre_serie <=> NEW.nombre_serie) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('serie', 'UPDATE', CAST(NEW.id_serie AS CHAR),
    JSON_OBJECT(
      'id_serie', OLD.id_serie,
      'nombre_serie', OLD.nombre_serie),
    JSON_OBJECT(
      'id_serie', NEW.id_serie,
      'nombre_serie', NEW.nombre_serie),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_serie_ad$$
CREATE TRIGGER trg_serie_ad AFTER DELETE ON serie
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('serie', 'DELETE', CAST(OLD.id_serie AS CHAR),
    JSON_OBJECT(
      'id_serie', OLD.id_serie,
      'nombre_serie', OLD.nombre_serie),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_libro_ai$$
CREATE TRIGGER trg_libro_ai AFTER INSERT ON libro
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro', 'INSERT', CAST(NEW.id_libro AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_libro', NEW.id_libro,
      'titulo', NEW.titulo,
      'isbn', NEW.isbn,
      'isbn13', NEW.isbn13,
      'num_paginas', NEW.num_paginas,
      'fecha_publicacion', NEW.fecha_publicacion,
      'rating_promedio', NEW.rating_promedio,
      'cantidad_ratings', NEW.cantidad_ratings,
      'cantidad_resenas', NEW.cantidad_resenas,
      'id_editorial', NEW.id_editorial,
      'id_idioma', NEW.id_idioma),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_libro_au$$
CREATE TRIGGER trg_libro_au AFTER UPDATE ON libro
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_libro <=> NEW.id_libro AND OLD.titulo <=> NEW.titulo AND OLD.isbn <=> NEW.isbn AND OLD.isbn13 <=> NEW.isbn13 AND OLD.num_paginas <=> NEW.num_paginas AND OLD.fecha_publicacion <=> NEW.fecha_publicacion AND OLD.rating_promedio <=> NEW.rating_promedio AND OLD.cantidad_ratings <=> NEW.cantidad_ratings AND OLD.cantidad_resenas <=> NEW.cantidad_resenas AND OLD.id_editorial <=> NEW.id_editorial AND OLD.id_idioma <=> NEW.id_idioma) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro', 'UPDATE', CAST(NEW.id_libro AS CHAR),
    JSON_OBJECT(
      'id_libro', OLD.id_libro,
      'titulo', OLD.titulo,
      'isbn', OLD.isbn,
      'isbn13', OLD.isbn13,
      'num_paginas', OLD.num_paginas,
      'fecha_publicacion', OLD.fecha_publicacion,
      'rating_promedio', OLD.rating_promedio,
      'cantidad_ratings', OLD.cantidad_ratings,
      'cantidad_resenas', OLD.cantidad_resenas,
      'id_editorial', OLD.id_editorial,
      'id_idioma', OLD.id_idioma),
    JSON_OBJECT(
      'id_libro', NEW.id_libro,
      'titulo', NEW.titulo,
      'isbn', NEW.isbn,
      'isbn13', NEW.isbn13,
      'num_paginas', NEW.num_paginas,
      'fecha_publicacion', NEW.fecha_publicacion,
      'rating_promedio', NEW.rating_promedio,
      'cantidad_ratings', NEW.cantidad_ratings,
      'cantidad_resenas', NEW.cantidad_resenas,
      'id_editorial', NEW.id_editorial,
      'id_idioma', NEW.id_idioma),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_libro_ad$$
CREATE TRIGGER trg_libro_ad AFTER DELETE ON libro
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro', 'DELETE', CAST(OLD.id_libro AS CHAR),
    JSON_OBJECT(
      'id_libro', OLD.id_libro,
      'titulo', OLD.titulo,
      'isbn', OLD.isbn,
      'isbn13', OLD.isbn13,
      'num_paginas', OLD.num_paginas,
      'fecha_publicacion', OLD.fecha_publicacion,
      'rating_promedio', OLD.rating_promedio,
      'cantidad_ratings', OLD.cantidad_ratings,
      'cantidad_resenas', OLD.cantidad_resenas,
      'id_editorial', OLD.id_editorial,
      'id_idioma', OLD.id_idioma),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_libro_autor_ai$$
CREATE TRIGGER trg_libro_autor_ai AFTER INSERT ON libro_autor
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro_autor', 'INSERT', CONCAT_WS('|', NEW.id_libro, NEW.id_autor),
    NULL,
    JSON_OBJECT(
      'id_libro', NEW.id_libro,
      'id_autor', NEW.id_autor,
      'orden', NEW.orden),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_libro_autor_au$$
CREATE TRIGGER trg_libro_autor_au AFTER UPDATE ON libro_autor
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_libro <=> NEW.id_libro AND OLD.id_autor <=> NEW.id_autor AND OLD.orden <=> NEW.orden) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro_autor', 'UPDATE', CONCAT_WS('|', NEW.id_libro, NEW.id_autor),
    JSON_OBJECT(
      'id_libro', OLD.id_libro,
      'id_autor', OLD.id_autor,
      'orden', OLD.orden),
    JSON_OBJECT(
      'id_libro', NEW.id_libro,
      'id_autor', NEW.id_autor,
      'orden', NEW.orden),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_libro_autor_ad$$
CREATE TRIGGER trg_libro_autor_ad AFTER DELETE ON libro_autor
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro_autor', 'DELETE', CONCAT_WS('|', OLD.id_libro, OLD.id_autor),
    JSON_OBJECT(
      'id_libro', OLD.id_libro,
      'id_autor', OLD.id_autor,
      'orden', OLD.orden),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_libro_serie_ai$$
CREATE TRIGGER trg_libro_serie_ai AFTER INSERT ON libro_serie
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro_serie', 'INSERT', CONCAT_WS('|', NEW.id_libro, NEW.id_serie),
    NULL,
    JSON_OBJECT(
      'id_libro', NEW.id_libro,
      'id_serie', NEW.id_serie,
      'numero_en_serie', NEW.numero_en_serie),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_libro_serie_au$$
CREATE TRIGGER trg_libro_serie_au AFTER UPDATE ON libro_serie
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_libro <=> NEW.id_libro AND OLD.id_serie <=> NEW.id_serie AND OLD.numero_en_serie <=> NEW.numero_en_serie) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro_serie', 'UPDATE', CONCAT_WS('|', NEW.id_libro, NEW.id_serie),
    JSON_OBJECT(
      'id_libro', OLD.id_libro,
      'id_serie', OLD.id_serie,
      'numero_en_serie', OLD.numero_en_serie),
    JSON_OBJECT(
      'id_libro', NEW.id_libro,
      'id_serie', NEW.id_serie,
      'numero_en_serie', NEW.numero_en_serie),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_libro_serie_ad$$
CREATE TRIGGER trg_libro_serie_ad AFTER DELETE ON libro_serie
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('libro_serie', 'DELETE', CONCAT_WS('|', OLD.id_libro, OLD.id_serie),
    JSON_OBJECT(
      'id_libro', OLD.id_libro,
      'id_serie', OLD.id_serie,
      'numero_en_serie', OLD.numero_en_serie),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_rol_ai$$
CREATE TRIGGER trg_rol_ai AFTER INSERT ON rol
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('rol', 'INSERT', CAST(NEW.id_rol AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_rol', NEW.id_rol,
      'nombre_rol', NEW.nombre_rol,
      'descripcion', NEW.descripcion),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_rol_au$$
CREATE TRIGGER trg_rol_au AFTER UPDATE ON rol
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_rol <=> NEW.id_rol AND OLD.nombre_rol <=> NEW.nombre_rol AND OLD.descripcion <=> NEW.descripcion) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('rol', 'UPDATE', CAST(NEW.id_rol AS CHAR),
    JSON_OBJECT(
      'id_rol', OLD.id_rol,
      'nombre_rol', OLD.nombre_rol,
      'descripcion', OLD.descripcion),
    JSON_OBJECT(
      'id_rol', NEW.id_rol,
      'nombre_rol', NEW.nombre_rol,
      'descripcion', NEW.descripcion),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_rol_ad$$
CREATE TRIGGER trg_rol_ad AFTER DELETE ON rol
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('rol', 'DELETE', CAST(OLD.id_rol AS CHAR),
    JSON_OBJECT(
      'id_rol', OLD.id_rol,
      'nombre_rol', OLD.nombre_rol,
      'descripcion', OLD.descripcion),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_usuario_ai$$
CREATE TRIGGER trg_usuario_ai AFTER INSERT ON usuario
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('usuario', 'INSERT', CAST(NEW.id_usuario AS CHAR),
    NULL,
    JSON_OBJECT(
      'id_usuario', NEW.id_usuario,
      'nombre_usuario', NEW.nombre_usuario,
      'nombre_completo', NEW.nombre_completo,
      'id_rol', NEW.id_rol,
      'activo', NEW.activo,
      'fecha_creacion', NEW.fecha_creacion),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DROP TRIGGER IF EXISTS trg_usuario_au$$
CREATE TRIGGER trg_usuario_au AFTER UPDATE ON usuario
FOR EACH ROW
BEGIN
  IF NOT (OLD.id_usuario <=> NEW.id_usuario AND OLD.nombre_usuario <=> NEW.nombre_usuario AND OLD.nombre_completo <=> NEW.nombre_completo AND OLD.id_rol <=> NEW.id_rol AND OLD.activo <=> NEW.activo AND OLD.fecha_creacion <=> NEW.fecha_creacion) THEN
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('usuario', 'UPDATE', CAST(NEW.id_usuario AS CHAR),
    JSON_OBJECT(
      'id_usuario', OLD.id_usuario,
      'nombre_usuario', OLD.nombre_usuario,
      'nombre_completo', OLD.nombre_completo,
      'id_rol', OLD.id_rol,
      'activo', OLD.activo,
      'fecha_creacion', OLD.fecha_creacion),
    JSON_OBJECT(
      'id_usuario', NEW.id_usuario,
      'nombre_usuario', NEW.nombre_usuario,
      'nombre_completo', NEW.nombre_completo,
      'id_rol', NEW.id_rol,
      'activo', NEW.activo,
      'fecha_creacion', NEW.fecha_creacion),
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER());
  END IF;
END$$

DROP TRIGGER IF EXISTS trg_usuario_ad$$
CREATE TRIGGER trg_usuario_ad AFTER DELETE ON usuario
FOR EACH ROW
  INSERT INTO auditoria_datos
    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)
  VALUES ('usuario', 'DELETE', CAST(OLD.id_usuario AS CHAR),
    JSON_OBJECT(
      'id_usuario', OLD.id_usuario,
      'nombre_usuario', OLD.nombre_usuario,
      'nombre_completo', OLD.nombre_completo,
      'id_rol', OLD.id_rol,
      'activo', OLD.activo,
      'fecha_creacion', OLD.fecha_creacion),
    NULL,
    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())$$

DELIMITER ;
