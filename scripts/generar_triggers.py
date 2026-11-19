"""Genera db/03_triggers.sql: un trigger AFTER INSERT/UPDATE/DELETE por tabla (RF-15).

Cada trigger guarda en auditoria_datos la llave, los valores anterior y nuevo en JSON,
el usuario de la aplicacion (variable de sesion @app_user que fija la API) y la fecha.

Uso:  python scripts/generar_triggers.py
"""
from pathlib import Path

# tabla -> (columnas de la llave primaria, columnas auditadas)
TABLAS: dict[str, tuple[list[str], list[str]]] = {
    # Nomina
    "dependencia": (["id_dependencia"], ["id_dependencia", "nombre_dependencia"]),
    "cargo": (["id_cargo"], ["id_cargo", "nombre_cargo"]),
    "eps": (["id_eps"], ["id_eps", "nombre_eps"]),
    "arl": (["id_arl"], ["id_arl", "nombre_arl"]),
    "fondo_pension": (["id_fondo_pension"], ["id_fondo_pension", "nombre_fondo"]),
    "periodo": (["id_periodo"], ["id_periodo", "anio", "mes"]),
    "tipo_novedad": (["id_tipo_novedad"], ["id_tipo_novedad", "nombre_tipo"]),
    "parametro_nomina": (["id_parametro"], ["id_parametro", "clave", "valor", "descripcion"]),
    "empleado": (["codigo_empleado"], [
        "codigo_empleado", "primer_apellido", "segundo_apellido", "nombres", "fecha_ingreso",
        "salario", "id_dependencia", "id_cargo", "id_eps", "id_arl", "id_fondo_pension"]),
    "nomina_mensual": (["id_nomina"], [
        "id_nomina", "codigo_empleado", "id_periodo", "dias_trabajados", "bonificacion", "transporte"]),
    "novedad": (["id_novedad"], [
        "id_novedad", "id_nomina", "id_tipo_novedad", "fecha_inicio", "fecha_fin", "dias"]),
    # Entretenimiento
    "pelicula": (["id_pelicula"], ["id_pelicula", "titulo", "anio"]),
    "genero": (["id_genero"], ["id_genero", "nombre_genero"]),
    "pelicula_genero": (["id_pelicula", "id_genero"], ["id_pelicula", "id_genero"]),
    "editorial": (["id_editorial"], ["id_editorial", "nombre_editorial"]),
    "idioma": (["id_idioma"], ["id_idioma", "codigo_idioma"]),
    "autor": (["id_autor"], ["id_autor", "nombre_autor"]),
    "serie": (["id_serie"], ["id_serie", "nombre_serie"]),
    "libro": (["id_libro"], [
        "id_libro", "titulo", "isbn", "isbn13", "num_paginas", "fecha_publicacion",
        "rating_promedio", "cantidad_ratings", "cantidad_resenas", "id_editorial", "id_idioma"]),
    "libro_autor": (["id_libro", "id_autor"], ["id_libro", "id_autor", "orden"]),
    "libro_serie": (["id_libro", "id_serie"], ["id_libro", "id_serie", "numero_en_serie"]),
    # Seguridad (el hash de la contrasena nunca se copia a la auditoria)
    "rol": (["id_rol"], ["id_rol", "nombre_rol", "descripcion"]),
    "usuario": (["id_usuario"], [
        "id_usuario", "nombre_usuario", "nombre_completo", "id_rol", "activo", "fecha_creacion"]),
}

OPERACIONES = {"INSERT": ("ai", None, "NEW"), "UPDATE": ("au", "OLD", "NEW"), "DELETE": ("ad", "OLD", None)}


def json_obj(alias: str | None, cols: list[str]) -> str:
    if alias is None:
        return "NULL"
    pares = ",\n      ".join(f"'{c}', {alias}.{c}" for c in cols)
    return f"JSON_OBJECT(\n      {pares})"


def llave(alias: str, pk: list[str]) -> str:
    if len(pk) == 1:
        return f"CAST({alias}.{pk[0]} AS CHAR)"
    return "CONCAT_WS('|', " + ", ".join(f"{alias}.{c}" for c in pk) + ")"


def generar() -> str:
    out = [
        "-- EntreCOL+ - Triggers de auditoria (GENERADO por scripts/generar_triggers.py, no editar a mano)",
        "USE entrecol;",
        "DELIMITER $$",
        "",
    ]
    for tabla, (pk, cols) in TABLAS.items():
        for op, (suf, antes, despues) in OPERACIONES.items():
            alias = despues or antes
            insert = (
                f"  INSERT INTO auditoria_datos\n"
                f"    (tabla, operacion, llave, valores_antes, valores_despues, usuario_app, usuario_bd)\n"
                f"  VALUES ('{tabla}', '{op}', {llave(alias, pk)},\n"
                f"    {json_obj(antes, cols)},\n"
                f"    {json_obj(despues, cols)},\n"
                f"    COALESCE(@app_user, 'SISTEMA'), CURRENT_USER())"
            )
            if op == "UPDATE":
                # Una recarga con los mismos valores no es un cambio: no se audita
                iguales = " AND ".join(f"OLD.{c} <=> NEW.{c}" for c in cols)
                cuerpo = f"BEGIN\n  IF NOT ({iguales}) THEN\n{insert};\n  END IF;\nEND"
            else:
                cuerpo = insert
            out.append(f"DROP TRIGGER IF EXISTS trg_{tabla}_{suf}$$")
            out.append(f"CREATE TRIGGER trg_{tabla}_{suf} AFTER {op} ON {tabla}\nFOR EACH ROW\n{cuerpo}$$\n")
    out.append("DELIMITER ;")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent.parent / "db" / "03_triggers.sql"
    destino.write_text(generar(), encoding="utf-8")
    print(f"{len(TABLAS) * 3} triggers escritos en {destino}")
