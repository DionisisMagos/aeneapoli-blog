from pathlib import Path
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# .env (τοπικά) + env vars (production)
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://*.koyeb.app",
    ],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "posts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static files στην παραγωγή
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# DB: τοπικά SQLite, σε production παίρνει DATABASE_URL (Postgres)
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "el-gr"
TIME_ZONE = "Europe/Athens"
USE_I18N = True
USE_TZ = True

# ---------- Static / Media ----------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------- Cloudinary (Media) ----------
CLOUDINARY_URL_ENV = os.environ.get("CLOUDINARY_URL")
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

USE_CLOUDINARY = bool(
    CLOUDINARY_URL_ENV
    or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)
)

if USE_CLOUDINARY:
    # Πρόσθεσε τα apps ΜΟΝΟ αν δεν υπάρχουν ήδη (για να μην διπλασιαστούν)
    for app in ("cloudinary", "cloudinary_storage"):
        if app not in INSTALLED_APPS:
            INSTALLED_APPS.append(app)

    # Επιλογές αποθήκευσης / upload (ασφαλή https + αποφυγή συγκρούσεων ονομάτων)
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
        "SECURE": True,
        "UPLOAD_OPTIONS": {
            "folder": "aeneapoli/covers",
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
            "resource_type": "image",
        },
    }

# Νέος τρόπος (Django 4.2+/5.0)
STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USE_CLOUDINARY
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Συμβατότητα με libs που κοιτάνε ακόμα την παλιά ρύθμιση
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# πίσω από proxy (https)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Log errors στο console (φαίνονται στο Koyeb) ----
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.template": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "cloudinary": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
