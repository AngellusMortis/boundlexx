"""
Base settings to build other settings files upon.
"""
from datetime import timedelta
from pathlib import Path

import environ

ROOT_DIR = Path(__file__).parents[2]
# boundlexx/)
APPS_DIR = ROOT_DIR / "boundlexx"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = env("TZ", default="UTC")
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(ROOT_DIR / "locale")]

CACHES = {
    "default": {
        "BACKEND": "redis_lock.django_cache.RedisCache",
        "LOCATION": env("CACHE_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
ADMIN_APPS = [
    "boundlexx.admin.theme",
    "admin_tools",
    "admin_tools.theming",
    "admin_tools.menu",
    "admin_tools.dashboard",
    "boundlexx.admin.apps.BoundlexxAdminConfig",
    # "django.contrib.admin",
]
DJANGO_APPS = [
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "django_celery_beat",
    "django_celery_results",
    "rest_framework",
]

LOCAL_APPS = [
    "boundlexx.users.apps.UsersConfig",
    "boundlexx.celery",
    "boundlexx.boundless",
    "boundlexx.api",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = ADMIN_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "boundlexx.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "boundlexx.boundless.backends.BoundlessAuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"  # noqa: E501
    },
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                "admin_tools.template_loaders.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "boundlexx.utils.context_processors.settings_context",
            ],
        },
    }
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("admin", "test@example.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING_CONFIG = None
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "default": {
            "()": "logging.Formatter",
            "format": "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",  # noqa E501
        },
        "colored": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",  # noqa E501
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_EXPIRES = timedelta(days=7)
CELERY_CACHE_BACKEND = "default"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Your stuff...
# ------------------------------------------------------------------------------
ADMIN_TOOLS_MENU = "boundlexx.admin.menu.BoundlexxMenu"
ADMIN_TOOLS_INDEX_DASHBOARD = (
    "boundlexx.admin.dashboard.BoundlexxIndexDashboard"
)
ADMIN_TOOLS_APP_INDEX_DASHBOARD = (
    "boundlexx.admin.dashboard.BoundlexxAppIndexDashboard"
)
FLOWER_BASE_URL = env("FLOWER_BASE_URL")

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",  # noqa
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",  # noqa
    "PAGE_SIZE": 255,
}

REST_FRAMEWORK_EXTENSIONS = {
    "DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX": "",
}

SERVE_STATIC_FILES_DEV = env.bool("SERVE_STATIC_FILES_DEV", False)


# base URL for discovery server
BOUNDLESS_API_URL_BASE = env(
    "BOUNDLESS_API_URL_BASE", default="http://host.docker.internal:8950"
)
BOUNDLESS_ACCOUNTS_BASE_URL = "https://account.playboundless.com"
BOUNDLESS_USERNAME = env("BOUNDLESS_USERNAME")
BOUNDLESS_PASSWORD = env("BOUNDLESS_PASSWORD", default=None)
BOUNDLESS_DS_REQUIRES_AUTH = env.bool(
    "BOUNDLESS_DS_REQUIRES_AUTH", default=False
)

# number of seconds between calls to each world
BOUNDLESS_API_WORLD_DELAY = 1

# path to Boundless itemcolorstrings.dat
BOUNDLESS_ITEMS_FILE = "/boundless/assets/archetypes/itemcolorstrings.dat"
BOUNDLESS_COMPILED_ITEMS_FILE = (
    "/boundless/assets/archetypes/compileditems.msgpack"
)

# timeout for making an API request
BOUNDLESS_API_TIMEOUT = 5
BOUNDLESS_AUTH_AUTO_CREATE = True

# minutes
BOUNDLESS_MIN_ITEM_DELAY = 10
BOUNDLESS_BASE_ITEM_DELAY = 30
BOUNDLESS_POPULAR_ITEM_DELAY_OFFSET = 5
BOUNDLESS_INACTIVE_ITEM_DELAY_OFFSET = 10
BOUNDLESS_MAX_ITEM_DELAY = 360
BOUNDLESS_EXO_SEARCH_RADIUS = 10
BOUNDLESS_MAX_WORLD_ID = 1000
BOUNDLESS_MAX_SCAN_CHUNK = 50
BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING = [
    32800,  # Rough Amethyst
    32803,  # Rough Diamond
    32804,  # Rough Emerald
    32809,  # Rough Topaz
    32807,  # Rough Ruby
    32808,  # Rough Sapphire
    32806,  # Rough Rift
    32801,  # Rough Blink
    32785,  # Copper Ore
    32787,  # Iron Ore
    32788,  # Silver Ore
    32786,  # Gold Ore
    32789,  # Titanium Ore
    32779,  # Soft Coal
    32777,  # Medium Coal
    32778,  # Hard Coal
    33081,  # Small Fossil
    33082,  # Medium Fossil
    33083,  # Large Fossil
    33080,  # Ancient Tech Remnant
    33078,  # Ancient Tech Component
    33079,  # Ancient Tech Device
    32802,  # Rough Umbris
    32805,  # Rough Oortstone
    10775,  # Trumpet Root
    10774,  # Travller's Perch
    10776,  # Rosetta Nox
    10777,  # Desert Sword
    10778,  # Spineback Plant
    10779,  # Twisted Aloba
    10780,  # Stardrop Plant
    10781,  # Oortian's Staff
    10782,  # Basic Boulder
    10783,  # Beanstalk Boulder
    10784,  # Boulder Tower
    10785,  # Boulder Ring
    10786,  # Boulder Chip
    10787,  # Tapered Boulder
    10788,  # Mottled Tar Spot Fungus
    10789,  # Clustered Tongue Fungus
    10790,  # Branch Funnel Fungus
    10791,  # Tinted-Burst Fungus
    10792,  # Weeping Waxcap Fungus
    10793,  # Glow Cap Fungus
    11632,  # Oortian Rice
    11633,  # Oorum Wheat
    11634,  # Ancient Oat
    11642,  # Starberry Vine
    11636,  # Waxy Tuber Plant
    11644,  # Juicy Starberry Vine
    11641,  # Kranut Plant
    11635,  # Tuber Plant
    11643,  # Glossy Starberry Vine
    11637,  # Exotic Tuber Plant
    11645,  # Combustion Fraction
    11646,  # Kindling Mass
    11647,  # Goo
    33561,  # Pertrolim
    33562,  # Primordial Resin
]

API_PROTOCOL = env("API_PROTOCOL", default="http")

STEAM_USERNAME = env("STEAM_USERNAME", default=None)
STEAM_PASSWORD = env("STEAM_PASSWORD", default=None)
STEAM_SENTRY_DIR = "/app/.steam"
STEAM_APP_ID = 324510
STEAM_AUTH_SCRIPT = "/auth-ticket.js"
STEAM_AUTH_NODE_MODULES = "/usr/local/lib/node_modules"


if BOUNDLESS_DS_REQUIRES_AUTH:
    if not (BOUNDLESS_PASSWORD or STEAM_USERNAME or STEAM_PASSWORD):
        raise ValueError(
            "BOUNDLESS_PASSWORD, STEAM_USERNAME, and STEAM_PASSWORD required "
            "if the Boundless DS server requires auth"
        )
