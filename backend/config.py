"""Application configuration, read from environment variables.

Nothing secret is hardcoded here. For local development you can put values in
a `.env` file (see `.env.example`); on Render set them in the dashboard or via
`render.yaml`.
"""
import os
import secrets
import logging
from datetime import timedelta

try:  # python-dotenv is optional at runtime
    from dotenv import load_dotenv

    _here = os.path.dirname(os.path.abspath(__file__))
    # Look for .env in backend/ first, then the project root.
    load_dotenv(os.path.join(_here, ".env"))
    load_dotenv(os.path.join(os.path.dirname(_here), ".env"))
except ImportError:  # pragma: no cover
    pass

log = logging.getLogger(__name__)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")


def _bool(name, default=False):
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        # Render/Heroku style URLs use the "postgres://" scheme, which
        # SQLAlchemy 1.4+ no longer accepts.
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url

    path = os.environ.get("SQLITE_PATH", "").strip()
    if not path:
        path = os.path.join(BACKEND_DIR, "instance", "hostel.db")
    elif not os.path.isabs(path):
        path = os.path.join(BACKEND_DIR, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return "sqlite:///" + path


DEFAULT_DEV_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]


def build_config():
    app_env = os.environ.get("APP_ENV", "development").strip().lower()
    is_production = app_env == "production"

    secret_key = os.environ.get("SECRET_KEY", "").strip()
    if not secret_key:
        if is_production:
            raise RuntimeError(
                "SECRET_KEY environment variable is required when APP_ENV=production."
            )
        secret_key = secrets.token_hex(32)
        log.warning(
            "SECRET_KEY not set - using a random development key. "
            "Sessions will be invalidated whenever the server restarts."
        )

    origins_raw = os.environ.get("CORS_ORIGINS", "").strip()
    if origins_raw:
        cors_origins = [o.strip().rstrip("/") for o in origins_raw.split(",") if o.strip()]
    else:
        cors_origins = [] if is_production else list(DEFAULT_DEV_ORIGINS)

    samesite = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax").strip().capitalize()
    if samesite not in {"Lax", "Strict", "None"}:
        samesite = "Lax"

    return {
        "APP_ENV": app_env,
        "IS_PRODUCTION": is_production,
        "SECRET_KEY": secret_key,
        "SQLALCHEMY_DATABASE_URI": _database_url(),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
        "CORS_ORIGINS": cors_origins,
        "SESSION_COOKIE_HTTPONLY": True,
        # SameSite=None requires Secure, browsers reject it otherwise.
        "SESSION_COOKIE_SECURE": _bool("SESSION_COOKIE_SECURE", is_production) or samesite == "None",
        "SESSION_COOKIE_SAMESITE": samesite,
        "PERMANENT_SESSION_LIFETIME": timedelta(
            hours=int(os.environ.get("SESSION_LIFETIME_HOURS", "8"))
        ),
        "MAX_CONTENT_LENGTH": 1 * 1024 * 1024,  # 1 MB request bodies are plenty
        "JSON_SORT_KEYS": False,
        "SERVE_FRONTEND": _bool("SERVE_FRONTEND", True),
    }
