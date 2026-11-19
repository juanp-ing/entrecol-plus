"""Captcha del inicio de sesion (RF-01).

Modo "local": la API dibuja una imagen con un texto aleatorio y guarda la respuesta en memoria
(un solo uso, 5 minutos). Modo "recaptcha": valida el token de Google reCAPTCHA v2.
"""
import base64
import io
import json
import random
import secrets
import string
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import settings

_ALFABETO = "".join(c for c in string.ascii_uppercase + string.digits if c not in "O0I1L")
_VIGENCIA_S = 300
_pendientes: dict[str, tuple[str, float]] = {}


def _fuente(tam: int) -> ImageFont.ImageFont:
    for nombre in ("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default(size=tam)


def _limpiar() -> None:
    ahora = time.time()
    for k in [k for k, (_, exp) in _pendientes.items() if exp < ahora]:
        _pendientes.pop(k, None)


def nuevo_captcha() -> dict:
    _limpiar()
    texto = "".join(random.choices(_ALFABETO, k=5))
    img = Image.new("RGB", (180, 60), (238, 242, 247))
    d = ImageDraw.Draw(img)
    for _ in range(8):
        d.line([(random.randint(0, 180), random.randint(0, 60)) for _ in range(2)],
               fill=(random.randint(120, 200),) * 3, width=2)
    f = _fuente(34)
    for i, ch in enumerate(texto):
        capa = Image.new("RGBA", (40, 50), (0, 0, 0, 0))
        ImageDraw.Draw(capa).text((4, 2), ch, font=f, fill=(30, 40, random.randint(80, 160)))
        capa = capa.rotate(random.randint(-25, 25), expand=False)
        img.paste(capa, (10 + i * 32, random.randint(2, 10)), capa)
    img = img.filter(ImageFilter.SMOOTH)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    cid = secrets.token_urlsafe(16)
    _pendientes[cid] = (texto, time.time() + _VIGENCIA_S)
    return {"captcha_id": cid, "imagen": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}


def validar_local(cid: str | None, respuesta: str | None) -> bool:
    if not cid or not respuesta:
        return False
    esperado = _pendientes.pop(cid, None)  # un solo intento por captcha
    if not esperado or esperado[1] < time.time():
        return False
    return secrets.compare_digest(esperado[0], respuesta.strip().upper())


def validar_recaptcha(token: str | None, ip: str | None) -> bool:
    if not token:
        return False
    datos = urllib.parse.urlencode(
        {"secret": settings.recaptcha_secret, "response": token, "remoteip": ip or ""}).encode()
    try:
        with urllib.request.urlopen("https://www.google.com/recaptcha/api/siteverify", datos, timeout=5) as r:
            return bool(json.load(r).get("success"))
    except OSError:
        return False


def validar(cid: str | None, respuesta: str | None, ip: str | None) -> bool:
    if settings.captcha_modo == "recaptcha":
        return validar_recaptcha(respuesta, ip)
    return validar_local(cid, respuesta)
