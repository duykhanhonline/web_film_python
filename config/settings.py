import sys
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    BRAND_NAME=(str, "PhimHay"),
)
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
TESTING = "test" in sys.argv[1:2]

BRAND_NAME = env("BRAND_NAME")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.accounts",
    "apps.catalog",
    "apps.player",
    "apps.billing",
    "apps.ads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Debug Toolbar is a dev-only dependency (requirements-dev.txt)
if DEBUG and not TESTING:
    try:
        import debug_toolbar  # noqa: F401
    except ImportError:
        pass
    else:
        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# MySQL 8+ with utf8mb4 so Vietnamese text and emoji store correctly
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"].setdefault("OPTIONS", {}).update(
    {
        "charset": "utf8mb4",
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    }
)
DATABASES["default"]["TEST"] = {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_0900_ai_ci"}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Cache: Redis only when REDIS_URL is set (production). Development without it
# gets no cache, so admin edits show at once. Tests use memory to test caching.
REDIS_URL = env("REDIS_URL", default="")
if TESTING:
    _cache = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
elif REDIS_URL:
    _cache = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "phimhay",
    }
elif DEBUG:
    _cache = {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
else:
    _cache = {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
CACHES = {"default": _cache}
HOME_CACHE_SECONDS = env.int("HOME_CACHE_SECONDS", default=60)

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
DATE_FORMAT = "d/m/Y"

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Dev/tests serve straight from static/ (no collectstatic needed)
WHITENOISE_AUTOREFRESH = DEBUG or TESTING
WHITENOISE_USE_FINDERS = DEBUG or TESTING
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG or TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

# Uploaded images: max size in bytes (see apps/catalog/validators.py)
MAX_IMAGE_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_TRAILER_UPLOAD_BYTES = 30 * 1024 * 1024

# Demo OTP code, accepted only when DEBUG is on (never sends SMS)
DEMO_OTP_CODE = "123456"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
