"""Crea (o restablece) un usuario de la aplicacion con contrasena cifrada en bcrypt.

Uso (desde la raiz del proyecto):
    uv run python scripts/crear_admin.py                      -> pregunta los datos
    uv run python scripts/crear_admin.py admin "Administrador" ADMINISTRADOR
"""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.db import consultar_uno, ejecutar  # noqa: E402
from app.seguridad import hash_password  # noqa: E402


def main() -> None:
    args = sys.argv[1:]
    usuario = args[0] if args else input("Usuario [admin]: ").strip() or "admin"
    nombre = args[1] if len(args) > 1 else input("Nombre completo [Administrador]: ").strip() or "Administrador"
    rol = (args[2] if len(args) > 2 else input("Rol ADMINISTRADOR/CONSULTA [ADMINISTRADOR]: ").strip() or "ADMINISTRADOR").upper()
    clave = getpass.getpass("Contrasena (min. 8): ")
    if len(clave) < 8 or clave != getpass.getpass("Repita la contrasena: "):
        sys.exit("La contrasena no coincide o tiene menos de 8 caracteres")

    r = consultar_uno("SELECT id_rol FROM rol WHERE nombre_rol = %s", (rol,))
    if not r:
        sys.exit(f"Rol desconocido: {rol}")
    ejecutar(
        """INSERT INTO usuario (nombre_usuario, nombre_completo, password_hash, id_rol)
           VALUES (%s, %s, %s, %s)
           ON DUPLICATE KEY UPDATE nombre_completo = VALUES(nombre_completo),
             password_hash = VALUES(password_hash), id_rol = VALUES(id_rol), activo = 1""",
        (usuario, nombre, hash_password(clave), r["id_rol"]),
        usuario="SISTEMA",
    )
    print(f"Usuario '{usuario}' listo con rol {rol}")


if __name__ == "__main__":
    main()
