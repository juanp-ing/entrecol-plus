"""Inicio y cierre de sesion (RF-01 a RF-04, RF-16)."""
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status

from .. import captcha
from ..auditoria import registrar_evento
from ..config import settings
from ..db import consultar_uno
from ..seguridad import Usuario, crear_token, usuario_actual, verificar_password

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])


@router.get("/captcha")
def obtener_captcha():
    if settings.captcha_modo == "recaptcha":
        return {"modo": "recaptcha", "site_key": settings.recaptcha_site_key}
    return {"modo": "local", **captcha.nuevo_captcha()}


@router.post("/login")
def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    captcha_respuesta: Annotated[str, Form()] = "",
    captcha_id: Annotated[str, Form()] = "",
):
    """Flujo de contrasena de OAuth 2.0 con captcha adicional. Devuelve un JWT."""
    ip = request.client.host if request.client else None
    if not captcha.validar(captcha_id, captcha_respuesta, ip):
        registrar_evento("LOGIN_FALLIDO", username, "Captcha incorrecto", ip)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El captcha es incorrecto o expiro")

    fila = consultar_uno(
        """SELECT u.id_usuario, u.nombre_usuario, u.nombre_completo, u.password_hash, u.activo, r.nombre_rol
             FROM usuario u
             JOIN rol r ON r.id_rol = u.id_rol
            WHERE u.nombre_usuario = %s""",
        (username,),
        usuario=username,
    )
    if not fila or not fila["activo"] or not verificar_password(password, fila["password_hash"]):
        registrar_evento("LOGIN_FALLIDO", username, "Usuario o contrasena incorrectos", ip)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contrasena incorrectos")

    u = Usuario(id=fila["id_usuario"], usuario=fila["nombre_usuario"],
                nombre=fila["nombre_completo"], rol=fila["nombre_rol"])
    registrar_evento("LOGIN_OK", u.usuario, None, ip)
    return {"access_token": crear_token(u), "token_type": "bearer", "usuario": u.model_dump()}


@router.post("/logout")
def logout(request: Request, u: Usuario = Depends(usuario_actual)):
    # JWT no guarda estado: el navegador descarta el token y aqui queda la traza.
    registrar_evento("LOGOUT", u.usuario, None, request.client.host if request.client else None)
    return {"ok": True}


@router.get("/yo", response_model=Usuario)
def yo(u: Usuario = Depends(usuario_actual)):
    return u
