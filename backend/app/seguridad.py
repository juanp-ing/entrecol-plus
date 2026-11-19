"""Contrasenas con bcrypt (RF-02), tokens JWT (RF-03) y control por rol (RF-04, RNF-03)."""
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .config import settings

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

ADMIN = "ADMINISTRADOR"
CONSULTA = "CONSULTA"


class Usuario(BaseModel):
    id: int
    usuario: str
    nombre: str
    rol: str


def hash_password(plano: str) -> str:
    return bcrypt.hashpw(plano.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("ascii")


def verificar_password(plano: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plano.encode("utf-8"), hashed.encode("ascii"))
    except ValueError:
        return False


def crear_token(u: Usuario) -> str:
    ahora = datetime.now(UTC)
    payload = {
        "sub": u.usuario,
        "uid": u.id,
        "nombre": u.nombre,
        "rol": u.rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.jwt_minutos),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str) -> Usuario:
    try:
        p = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algoritmo])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesion expiro, inicie sesion de nuevo")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalido")
    return Usuario(id=p["uid"], usuario=p["sub"], nombre=p["nombre"], rol=p["rol"])


def usuario_actual(request: Request, token: str = Depends(oauth2)) -> Usuario:
    u = decodificar_token(token)
    request.state.usuario = u.usuario  # lo usa el middleware de auditoria
    return u


def requiere_admin(u: Usuario = Depends(usuario_actual)) -> Usuario:
    if u.rol != ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el administrador puede realizar esta accion")
    return u
