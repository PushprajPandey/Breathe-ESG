import dj_database_url
from decouple import config

from .base import *  # noqa: F403, F405


def _split_hosts(value: str) -> list[str]:
    """ALLOWED_HOSTS must be hostnames only — no https:// or paths."""
    hosts = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        part = part.replace("https://", "").replace("http://", "")
        part = part.split("/")[0].strip()
        if part:
            hosts.append(part)
    return hosts


def _split_cors_origins(value: str) -> list[str]:
    """CORS origins must be scheme + host only — no trailing slash (django-cors-headers E014)."""
    origins = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        part = part.rstrip("/")
        if "://" not in part:
            part = f"https://{part}"
        origins.append(part)
    return origins


DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = _split_hosts(config("ALLOWED_HOSTS", default=""))
# Render free-tier hostnames include random suffixes (e.g. breathe-esg-api-8mre.onrender.com)
if ALLOWED_HOSTS and ".onrender.com" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".onrender.com")
elif not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [".onrender.com"]

DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

CORS_ALLOWED_ORIGINS = _split_cors_origins(config("CORS_ALLOWED_ORIGINS", default=""))
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
