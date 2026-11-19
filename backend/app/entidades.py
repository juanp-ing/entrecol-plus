"""Catalogo de entidades del CRUD (RF-11).

Cada entidad declara su tabla, su llave, sus campos editables y la consulta de listado escrita a mano.
Los nombres de tabla y columna salen SOLO de este archivo (lista blanca); los valores del usuario
siempre viajan como parametros.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Campo:
    nombre: str
    etiqueta: str
    tipo: str = "texto"  # texto | entero | decimal | fecha | password | bool
    requerido: bool = True
    fk: str | None = None  # entidad de la que se toman las opciones
    auto: bool = False  # llave AUTO_INCREMENT: no se pide al crear


@dataclass(frozen=True)
class Entidad:
    clave: str
    titulo: str
    tabla: str
    pk: str
    campos: list[Campo]
    listado: str  # SELECT ... con alias "id" y "etiqueta" para combos; sin WHERE/ORDER/LIMIT
    busqueda: str  # expresion SQL sobre la que filtra el buscador
    orden: str
    modulo: str = "Nomina"
    admin_lectura: bool = False  # solo el administrador puede verla (usuarios)
    extras: dict = field(default_factory=dict)


def _catalogo(clave, titulo, tabla, pk, col, etiqueta, modulo="Nomina"):
    return Entidad(
        clave, titulo, tabla, pk,
        [Campo(pk, "ID", "entero", auto=True), Campo(col, etiqueta)],
        f"SELECT {pk} AS id, {col} AS etiqueta, {pk}, {col} FROM {tabla}",
        col, f"{col} ASC", modulo,
    )


ENTIDADES: dict[str, Entidad] = {e.clave: e for e in [
    _catalogo("dependencias", "Dependencias", "dependencia", "id_dependencia", "nombre_dependencia", "Dependencia"),
    _catalogo("cargos", "Cargos", "cargo", "id_cargo", "nombre_cargo", "Cargo"),
    _catalogo("eps", "EPS", "eps", "id_eps", "nombre_eps", "EPS"),
    _catalogo("arl", "ARL", "arl", "id_arl", "nombre_arl", "ARL"),
    _catalogo("fondos", "Fondos de pension", "fondo_pension", "id_fondo_pension", "nombre_fondo", "Fondo"),
    _catalogo("tipos-novedad", "Tipos de novedad", "tipo_novedad", "id_tipo_novedad", "nombre_tipo", "Tipo"),
    Entidad(
        "empleados", "Empleados", "empleado", "codigo_empleado",
        [
            Campo("codigo_empleado", "Codigo", "entero"),
            Campo("primer_apellido", "Primer apellido"),
            Campo("segundo_apellido", "Segundo apellido", requerido=False),
            Campo("nombres", "Nombres"),
            Campo("fecha_ingreso", "Fecha de ingreso", "fecha"),
            Campo("salario", "Salario", "decimal"),
            Campo("id_dependencia", "Dependencia", "entero", fk="dependencias"),
            Campo("id_cargo", "Cargo", "entero", fk="cargos"),
            Campo("id_eps", "EPS", "entero", fk="eps"),
            Campo("id_arl", "ARL", "entero", fk="arl"),
            Campo("id_fondo_pension", "Fondo de pension", "entero", fk="fondos"),
        ],
        """SELECT e.codigo_empleado AS id,
                  CONCAT_WS(' ', e.primer_apellido, e.segundo_apellido, e.nombres) AS etiqueta,
                  e.*, d.nombre_dependencia, c.nombre_cargo, s.nombre_eps, a.nombre_arl, f.nombre_fondo
             FROM empleado e
             JOIN dependencia d   ON d.id_dependencia = e.id_dependencia
             JOIN cargo c         ON c.id_cargo = e.id_cargo
             JOIN eps s           ON s.id_eps = e.id_eps
             JOIN arl a           ON a.id_arl = e.id_arl
             JOIN fondo_pension f ON f.id_fondo_pension = e.id_fondo_pension""",
        "CONCAT_WS(' ', e.primer_apellido, e.segundo_apellido, e.nombres, e.codigo_empleado)",
        "e.primer_apellido ASC, e.segundo_apellido ASC, e.nombres ASC",
    ),
    Entidad(
        "periodos", "Periodos", "periodo", "id_periodo",
        [Campo("id_periodo", "ID", "entero", auto=True), Campo("anio", "Ano", "entero"), Campo("mes", "Mes", "entero")],
        "SELECT id_periodo AS id, CONCAT(LPAD(mes, 2, '0'), '/', anio) AS etiqueta, id_periodo, anio, mes FROM periodo",
        "CONCAT(LPAD(mes, 2, '0'), '/', anio)", "anio DESC, mes DESC",
    ),
    Entidad(
        "nominas", "Liquidaciones mensuales", "nomina_mensual", "id_nomina",
        [
            Campo("id_nomina", "ID", "entero", auto=True),
            Campo("codigo_empleado", "Empleado", "entero", fk="empleados"),
            Campo("id_periodo", "Periodo", "entero", fk="periodos"),
            Campo("dias_trabajados", "Dias trabajados", "entero"),
            Campo("bonificacion", "Bonificacion", "decimal"),
            Campo("transporte", "Transporte", "decimal"),
        ],
        """SELECT n.id_nomina AS id,
                  CONCAT(e.codigo_empleado, ' - ', LPAD(p.mes, 2, '0'), '/', p.anio) AS etiqueta,
                  n.*, CONCAT_WS(' ', e.primer_apellido, e.segundo_apellido, e.nombres) AS empleado,
                  CONCAT(LPAD(p.mes, 2, '0'), '/', p.anio) AS periodo
             FROM nomina_mensual n
             JOIN empleado e ON e.codigo_empleado = n.codigo_empleado
             JOIN periodo p  ON p.id_periodo = n.id_periodo""",
        "CONCAT_WS(' ', e.primer_apellido, e.nombres, e.codigo_empleado)",
        "p.anio DESC, p.mes DESC, e.primer_apellido ASC",
    ),
    Entidad(
        "novedades", "Novedades", "novedad", "id_novedad",
        [
            Campo("id_novedad", "ID", "entero", auto=True),
            Campo("id_nomina", "Liquidacion", "entero", fk="nominas"),
            Campo("id_tipo_novedad", "Tipo", "entero", fk="tipos-novedad"),
            Campo("fecha_inicio", "Fecha inicio", "fecha"),
            Campo("fecha_fin", "Fecha fin", "fecha"),
            Campo("dias", "Dias", "entero"),
        ],
        """SELECT v.id_novedad AS id, CONCAT(t.nombre_tipo, ' ', v.fecha_inicio) AS etiqueta,
                  v.*, t.nombre_tipo, e.codigo_empleado,
                  CONCAT_WS(' ', e.primer_apellido, e.segundo_apellido, e.nombres) AS empleado
             FROM novedad v
             JOIN tipo_novedad t   ON t.id_tipo_novedad = v.id_tipo_novedad
             JOIN nomina_mensual n ON n.id_nomina = v.id_nomina
             JOIN empleado e       ON e.codigo_empleado = n.codigo_empleado""",
        "CONCAT_WS(' ', e.primer_apellido, e.nombres, t.nombre_tipo)",
        "v.fecha_inicio DESC",
    ),
    Entidad(
        "parametros", "Parametros de nomina", "parametro_nomina", "id_parametro",
        [
            Campo("id_parametro", "ID", "entero", auto=True), Campo("clave", "Clave"),
            Campo("valor", "Valor", "decimal"), Campo("descripcion", "Descripcion", requerido=False),
        ],
        "SELECT id_parametro AS id, clave AS etiqueta, id_parametro, clave, valor, descripcion FROM parametro_nomina",
        "clave", "clave ASC",
    ),
    # --- Entretenimiento ---
    Entidad(
        "peliculas", "Peliculas", "pelicula", "id_pelicula",
        [Campo("id_pelicula", "ID", "entero"), Campo("titulo", "Titulo"), Campo("anio", "Ano", "entero")],
        """SELECT p.id_pelicula AS id, p.titulo AS etiqueta, p.id_pelicula, p.titulo, p.anio,
                  (SELECT GROUP_CONCAT(g.nombre_genero ORDER BY g.nombre_genero SEPARATOR ', ')
                     FROM pelicula_genero pg JOIN genero g ON g.id_genero = pg.id_genero
                    WHERE pg.id_pelicula = p.id_pelicula) AS generos
             FROM pelicula p""",
        "p.titulo", "p.titulo ASC", "Entretenimiento",
    ),
    _catalogo("generos", "Generos", "genero", "id_genero", "nombre_genero", "Genero", "Entretenimiento"),
    Entidad(
        "peliculas-generos", "Generos por pelicula", "pelicula_genero", "id_pelicula,id_genero",
        [Campo("id_pelicula", "Pelicula", "entero", fk="peliculas"), Campo("id_genero", "Genero", "entero", fk="generos")],
        """SELECT CONCAT(pg.id_pelicula, ',', pg.id_genero) AS id, p.titulo AS etiqueta,
                  pg.id_pelicula, pg.id_genero, p.titulo, g.nombre_genero
             FROM pelicula_genero pg
             JOIN pelicula p ON p.id_pelicula = pg.id_pelicula
             JOIN genero g   ON g.id_genero = pg.id_genero""",
        "CONCAT_WS(' ', p.titulo, g.nombre_genero)", "p.titulo ASC", "Entretenimiento",
    ),
    Entidad(
        "libros", "Libros", "libro", "id_libro",
        [
            Campo("id_libro", "ID", "entero"), Campo("titulo", "Titulo"),
            Campo("isbn", "ISBN", requerido=False), Campo("isbn13", "ISBN-13", requerido=False),
            Campo("num_paginas", "Paginas", "entero", requerido=False),
            Campo("fecha_publicacion", "Fecha de publicacion", "fecha", requerido=False),
            Campo("rating_promedio", "Calificacion", "decimal", requerido=False),
            Campo("cantidad_ratings", "Cantidad de calificaciones", "entero"),
            Campo("cantidad_resenas", "Cantidad de resenas", "entero"),
            Campo("id_editorial", "Editorial", "entero", fk="editoriales"),
            Campo("id_idioma", "Idioma", "entero", fk="idiomas"),
        ],
        """SELECT l.id_libro AS id, l.titulo AS etiqueta, l.*, ed.nombre_editorial, i.codigo_idioma,
                  (SELECT GROUP_CONCAT(a.nombre_autor ORDER BY la.orden SEPARATOR ', ')
                     FROM libro_autor la JOIN autor a ON a.id_autor = la.id_autor
                    WHERE la.id_libro = l.id_libro) AS autores
             FROM libro l
             JOIN editorial ed ON ed.id_editorial = l.id_editorial
             JOIN idioma i     ON i.id_idioma = l.id_idioma""",
        "CONCAT_WS(' ', l.titulo, l.isbn, l.isbn13)", "l.titulo ASC", "Entretenimiento",
    ),
    _catalogo("autores", "Autores", "autor", "id_autor", "nombre_autor", "Autor", "Entretenimiento"),
    _catalogo("editoriales", "Editoriales", "editorial", "id_editorial", "nombre_editorial", "Editorial", "Entretenimiento"),
    _catalogo("idiomas", "Idiomas", "idioma", "id_idioma", "codigo_idioma", "Codigo", "Entretenimiento"),
    _catalogo("series", "Series", "serie", "id_serie", "nombre_serie", "Serie", "Entretenimiento"),
    # --- Seguridad ---
    Entidad(
        "usuarios", "Usuarios", "usuario", "id_usuario",
        [
            Campo("id_usuario", "ID", "entero", auto=True),
            Campo("nombre_usuario", "Usuario"),
            Campo("nombre_completo", "Nombre completo"),
            Campo("password", "Contrasena", "password", requerido=False),
            Campo("id_rol", "Rol", "entero", fk="roles"),
            Campo("activo", "Activo", "bool"),
        ],
        """SELECT u.id_usuario AS id, u.nombre_usuario AS etiqueta, u.id_usuario, u.nombre_usuario,
                  u.nombre_completo, u.id_rol, u.activo, u.fecha_creacion, r.nombre_rol
             FROM usuario u JOIN rol r ON r.id_rol = u.id_rol""",
        "CONCAT_WS(' ', u.nombre_usuario, u.nombre_completo)", "u.nombre_usuario ASC",
        "Seguridad", admin_lectura=True,
    ),
    Entidad(
        "roles", "Roles", "rol", "id_rol",
        [Campo("id_rol", "ID", "entero", auto=True), Campo("nombre_rol", "Rol")],
        "SELECT id_rol AS id, nombre_rol AS etiqueta, id_rol, nombre_rol, descripcion FROM rol",
        "nombre_rol", "nombre_rol ASC", "Seguridad", admin_lectura=True, extras={"solo_lectura": True},
    ),
]}
