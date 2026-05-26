import dj_database_url
from decouple import config

from .base import *  # noqa: F403, F405

DEBUG = False
SECRET_KEY = config("SECRET_KEY")
_hosts = config("ALLOWED_HOSTS", default="")
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

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

_cors = config("CORS_ALLOWED_ORIGINS", default="")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Manifest storage can fail deploy if collectstatic misses a file; use compressed files only.
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
