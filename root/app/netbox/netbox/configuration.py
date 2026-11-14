import os
from pathlib import Path

CONFIG_DIR = Path("/config")

def env(name, default=""):
    """NAME, or the contents of NAME_FILE (podman secrets)."""
    path = os.environ.get(f"{name}_FILE")
    if path:
        return Path(path).read_text().strip()
    return os.environ.get(name, default)

def secret(name, filename):
    val = env(name)
    if val:
        return val
    f = CONFIG_DIR / filename
    return f.read_text().strip() if f.exists() else ""

def as_bool(v):
    return str(v).lower() in ("1", "true", "yes", "on")

ALLOWED_HOSTS = env("ALLOWED_HOSTS", "*").split()
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS").split()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "netbox"),
        "USER": env("DB_USER", "netbox"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", "postgres"),
        "PORT": env("DB_PORT", ""),
        "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", "300")),
    }
}

def _redis(db_var, default_db):
    return {
        "HOST": env("REDIS_HOST", "redis"),
        "PORT": int(env("REDIS_PORT", "6379")),
        "PASSWORD": env("REDIS_PASSWORD"),
        "DATABASE": int(env(db_var, default_db)),
        "SSL": as_bool(env("REDIS_SSL", "false")),
    }

# tasks and caching must use different DB IDs
REDIS = {"tasks": _redis("REDIS_DB_TASKS", "0"),
         "caching": _redis("REDIS_DB_CACHE", "1")}

SECRET_KEY = secret("NETBOX_SECRET_KEY", "secret_key")
_pepper = secret("NETBOX_API_TOKEN_PEPPER", "api_token_pepper")
API_TOKEN_PEPPERS = {1: _pepper} if _pepper else {}

TIME_ZONE = env("TZ", "UTC")
MEDIA_ROOT = str(CONFIG_DIR / "media")
SCRIPTS_ROOT = str(CONFIG_DIR / "scripts")
DEBUG = as_bool(env("DEBUG", "false"))

# Anything else (PLUGINS, LDAP, SSO...) goes in /config/configuration_extra.py
_extra = CONFIG_DIR / "configuration_extra.py"
if _extra.exists():
    exec(compile(_extra.read_text(), str(_extra), "exec"))

