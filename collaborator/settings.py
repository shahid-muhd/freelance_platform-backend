"""
Django settings for collaborator project.

Generated by 'django-admin startproject' using Django 4.1.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta
import mongoengine
from dotenv import load_dotenv
from celery.schedules import crontab


load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-7m0_5-x$att+wt^l$w^_mp+=4u4!f01mmp&1hvg(e=kwocz&x&"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['13.234.114.90','0.0.0.0','starfiled.xyz','www.starfiled.xyz','localhost']


# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "channels",
    "rest_framework",
    "accounts",
    "projects",
    "administration",
    "work_profiles",
    "payments",
    "communication",
    "rest_framework_simplejwt.token_blacklist",
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://starfiled.xyz",
    "http://loomixcollaborator-9x6wxxyav-shahids-projects-93b8fcca.vercel.app",
    "http://loomixtechnologies.xyz"
]


CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://starfiled.xyz",
    "http://loomixcollaborator-9x6wxxyav-shahids-projects-93b8fcca.vercel.app",
    "http://loomixtechnologies.xyz"
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

AUTH_USER_MODEL = "accounts.CustomUser"
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middlewares.block_middleware.BlockMiddleWare",
]


ROOT_URLCONF = "collaborator.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("localhost", 6379)],
#         },
#     },
# }
ASGI_APPLICATION = "collaborator.asgi.application"
# WSGI_APPLICATION = "collaborator.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PSQL_DB_NAME"),
        "USER": os.getenv("PSQL_USERNAME"),
        "PASSWORD": os.getenv("PSQL_PASSWORD"),
        "HOST": os.getenv("PSQL_HOST"),
    }
}

MONGO_URI = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@cluster0.u7e6i35.mongodb.net/{os.environ['MONGO_DB_NAME']}?retryWrites=true&w=majority&appName=Cluster0"
mongoengine.connect(host=MONGO_URI)

# mongoengine.connect(
#     db="loomix_jobs", host="localhost", username="shahid", password="shahid123"
# )


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
    "TOKEN_OBTAIN_SERIALIZER": "accounts.tokenSerializer.CustomTokenObtainPairSerializer",
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "shahid04m@gmail.com"
EMAIL_HOST_PASSWORD = "baev mket ozms vyhm"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 300  # in seconds
DEFAULT_FROM_EMAIL = "Loomix Jobs shahid04m@gmail.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")


CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# CELERY_BEAT_SCHEDULE = {
#     'check-subscription-expiry-every-day': {
#         'task': 'app.tasks.check_subscription_expiry',
#         'schedule': crontab(hour=10, minute=35),  # Run every day at midnight
#     },
# }


CELERY_BEAT_SCHEDULE = {
    "check-subscription-expiry-every-minute": {
        "task": "payments.tasks.check_subscription_expiry",
        "schedule": crontab(minute="*"),  # Run every minute
    },
}
