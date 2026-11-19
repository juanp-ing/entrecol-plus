"""Configuracion leida de .env (raiz del proyecto)."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=RAIZ / ".env", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "entrecol"
    db_user: str = "entrecol_app"
    db_password: str = ""

    jwt_secret: str = "cambiar"
    jwt_algoritmo: str = "HS256"
    jwt_minutos: int = 60

    captcha_modo: str = "local"  # local | recaptcha
    recaptcha_site_key: str = ""
    recaptcha_secret: str = ""


settings = Settings()
