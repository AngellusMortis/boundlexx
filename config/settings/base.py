"""
Base settings to build other settings files upon.
"""
from datetime import timedelta
from pathlib import Path

import environ

from config.huey_app import huey

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

ENABLE_PROMETHEUS = env.bool("ENABLE_PROMETHEUS", default=False)
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

if ENABLE_PROMETHEUS:
    DATABASES["default"]["ENGINE"] = "django_prometheus.db.backends.postgresql"
    CACHES["default"]["BACKEND"] = "boundlexx.utils.backends.RedisCache"

AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME", default=None)
AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY", default=None)
AZURE_CONTAINER = env("AZURE_CONTAINER", default=None)
AZURE_CONTAINER_PREFIX = env("AZURE_CONTAINER_PREFIX", default="local-")
AZURE_CUSTOM_DOMAIN = env("AZURE_CUSTOM_DOMAIN", default=None)
AZURE_FILENAME_PREFIX = env("AZURE_FILENAME_PREFIX", default=None)

AZURE_CDN_RESOURCE_GROUP = env("AZURE_CDN_RESOURCE_GROUP", default=None)
AZURE_CDN_PROFILE_NAME = env("AZURE_CDN_PROFILE_NAME", default=None)
AZURE_CDN_ENDPOINT_NAME = env("AZURE_CDN_ENDPOINT_NAME", default=None)
AZURE_CDN_DYNAMIC_PURGE = env.bool("AZURE_CDN_DYNAMIC_PURGE", False)
AZURE_STATIC_CDN_RESOURCE_GROUP = env(
    "AZURE_STATIC_CDN_RESOURCE_GROUP", default=AZURE_CDN_RESOURCE_GROUP
)
AZURE_STATIC_CDN_PROFILE_NAME = env(
    "AZURE_STATIC_CDN_PROFILE_NAME", default=AZURE_CDN_PROFILE_NAME
)
AZURE_STATIC_CDN_ENDPOINT_NAME = env(
    "AZURE_STATIC_CDN_ENDPOINT_NAME", default=AZURE_CDN_ENDPOINT_NAME
)
AZURE_CLIENT_ID = env("AZURE_CLIENT_ID", default=None)
AZURE_CLIENT_SECRET = env("AZURE_CLIENT_SECRET", default=None)
AZURE_TENANT_ID = env("AZURE_TENANT_ID", default=None)
AZURE_SUBSCRIPTION_ID = env("AZURE_SUBSCRIPTION_ID", default=None)

if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY and AZURE_CONTAINER:
    DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
ADMIN_APPS = [
    # "boundlexx.admin.theme",
    # "admin_tools",
    # "admin_tools.theming",
    # "admin_tools.menu",
    # "admin_tools.dashboard",
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
    "huey.contrib.djhuey",
    "django_celery_beat",
    "django_celery_results",
    "rest_framework",
    "rest_framework.authtoken",
    "django_json_widget",
    "corsheaders",
    "crispy_forms",
    "robots",
]

LOCAL_APPS = [
    "boundlexx.users",
    "boundlexx.celery",
    "boundlexx.boundless",
    "boundlexx.api",
    "boundlexx.notifications",
    "boundlexx.ingest",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = ADMIN_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

if ENABLE_PROMETHEUS:
    INSTALLED_APPS = ["django_prometheus"] + INSTALLED_APPS

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

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

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
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if ENABLE_PROMETHEUS:
    MIDDLEWARE = (
        ["django_prometheus.middleware.PrometheusBeforeMiddleware"]
        + MIDDLEWARE
        + ["django_prometheus.middleware.PrometheusAfterMiddleware"]
    )

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = env("STATIC_URL", default="/static/")
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
                # "admin_tools.template_loaders.Loader",
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
ADMINS = [("Angellus", "angellus@mort.is")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

CORS_ALLOW_ALL_ORIGINS = True

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "colored": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(levelname)s %(asctime)s %(name)s %(module)s "
            "%(process)d %(thread)d %(message)s",  # noqa E501
        },
        "huey_colored": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(levelname)s %(asctime)s %(name)s %(threadName)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
        "huey": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "huey_colored",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        "root": {"level": "INFO", "handlers": ["console"]},
        "ingest": {"level": "INFO", "handlers": ["console"]},
        "azure": {"level": "WARNING"},
        "huey": {"handlers": ["huey"], "propagate": False},
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
CELERY_ENABLE_UTC = True
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

# Huey
# ------------------------------------------------------------------------------
HUEY = huey

# Your stuff...
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",  # noqa
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "DEFAULT_PAGINATION_CLASS": "boundlexx.api.pagination.MaxLimitOffsetPagination",  # noqa
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],  # noqa
    "PAGE_SIZE": 100,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_msgpack.renderers.MessagePackRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1/minute",
        "anon": f"{int(env('API_RATE_LIMIT', default=10))}/second",
    },
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": "boundlexx.api.negotiation.IgnoreClientContentNegotiation",  # noqa: E501
}

REST_FRAMEWORK_EXTENSIONS = {
    "DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX": "",
}
CRISPY_TEMPLATE_PACK = "bootstrap4"

SERVE_STATIC_FILES_DEV = env.bool("SERVE_STATIC_FILES_DEV", False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_SSL", "on")

CACHE_DURATION = 60 * 60 * 24
ROBOTS_USE_SITEMAP = False


EMOJI_API_KEY = env("EMOJI_API_KEY", default=None)

# base URL for discovery server
BOUNDLESS_API_URL_BASE = env(
    "BOUNDLESS_API_URL_BASE", default="http://host.docker.internal:8950"
)
BOUNDLESS_ACCOUNTS_BASE_URL = "https://account.playboundless.com"
BOUNDLESS_USERNAMES = env.list("BOUNDLESS_USERNAMES", default=[])
BOUNDLESS_PASSWORDS = env.list("BOUNDLESS_PASSWORDS", default=[])
BOUNDLESS_DS_REQUIRES_AUTH = env.bool("BOUNDLESS_DS_REQUIRES_AUTH", default=False)

# number of seconds between calls to each world
BOUNDLESS_API_WORLD_DELAY = float(env("BOUNDLESS_API_WORLD_DELAY", default=1.0))
BOUNDLESS_API_DS_DELAY = float(env("BOUNDLESS_API_DS_DELAY", default=1.0))
BOUNDLESS_LOCATION = "/boundless/"
BOUNDLESS_WORLDS_LOCATIONS = "/boundless-worlds/"
BOUNDLESS_ICONS_LOCATION = "/boundless-icons/"
BOUNDLESS_ICONS_MAPPING = {
    11632: "ITEM_CROPDROP_RICE",
    11633: "ITEM_CROPDROP_WHEAT",
    11634: "ITEM_CROPDROP_OATS",
    11641: "ITEM_CROPDROP_NUTS",
    11646: "ITEM_CROPDROP_FUEL_ENRICHER",
    11645: "ITEM_CROPDROP_FUEL",
    11647: "ITEM_CROPDROP_DRIPSTONE",
    10703: "DECORATION_HALLOWEEN_BAT",
    13718: "DECORATION_HALLOWEEN_SPIDER",
    13812: "TOOL_SEASONAL_TOTEM_CANDY",
    11635: "FOOD_EARTHYAM_BASE_RAW",
    11637: "FOOD_EARTHYAM_EXOTIC_RAW",
    11636: "FOOD_EARTHYAM_WAXY_RAW",
    11642: "FOOD_STARBERRY_RAW",
    11643: "FOOD_STARBERRY_GLOSSY_RAW",
    11644: "FOOD_STARBERRY_JUICY_RAW",
}
BOUNDLESS_DEFAULT_COLORS = {
    # misc.
    33566: 228,
    # oortmas
    13812: 24,
    33570: 24,
    # goo
    11647: 228,
    32983: 228,
    32993: 228,
    # halloween
    10702: 1,
    10703: 1,
    13717: 1,
    13718: 1,
    # game defined
    10850: 28,
    9555: 87,
    9838: 25,
    9839: 82,
    9840: 60,
    9841: 93,
    10775: 93,
    10774: 25,
    10788: 25,
    10789: 93,
    10790: 93,
    10792: 60,
    10793: 93,
    10791: 25,
    3085: 82,
    6157: 87,
    13: 108,
    10814: 84,
    10870: 28,
    10842: 208,
    10806: 204,
    10866: 28,
    10846: 82,
    10779: 25,
    10778: 93,
    10781: 93,
    10776: 60,
    10780: 93,
    10777: 82,
    10798: 63,
    10794: 111,
    10802: 102,
    10810: 84,
    11588: 28,
    11592: 82,
    11584: 84,
    10854: 28,
    10858: 28,
    10862: 28,
    10830: 82,
    10822: 222,
    10818: 87,
    10838: 28,
    10834: 82,
    10826: 55,
}

# timeout for making an API request
BOUNDLESS_API_TIMEOUT = 5
BOUNDLESS_AUTH_AUTO_CREATE = True

# minutes
BOUNDLESS_API_KEY = env("BOUNDLESS_API_KEY", default=None)
BOUNDLESS_MAX_WORLDS_PER_POLL = int(env("BOUNDLESS_MAX_WORLDS_PER_POLL", default=100))
BOUNDLESS_MAX_PERM_WORLDS_PER_PRICE_POLL = int(
    env("BOUNDLESS_MAX_PERM_WORLDS_PER_PRICE_POLL", default=10)
)
BOUNDLESS_MAX_SOV_WORLDS_PER_PRICE_POLL = int(
    env("BOUNDLESS_MAX_SOV_WORLDS_PER_PRICE_POLL", default=100)
)
BOUNDLESS_MIN_ITEM_DELAY = int(env("BOUNDLESS_MIN_ITEM_DELAY", default=20))
BOUNDLESS_BASE_ITEM_DELAY = int(env("BOUNDLESS_BASE_ITEM_DELAY", default=60))
BOUNDLESS_POPULAR_ITEM_DELAY_OFFSET = int(
    env("BOUNDLESS_POPULAR_ITEM_DELAY_OFFSET", default=5)
)
BOUNDLESS_INACTIVE_ITEM_DELAY_OFFSET = int(
    env("BOUNDLESS_INACTIVE_ITEM_DELAY_OFFSET", default=30)
)
BOUNDLESS_MAX_ITEM_DELAY = int(env("BOUNDLESS_MAX_ITEM_DELAY", default=720))
BOUNDLESS_DEAD_ITEM_MULTIPLIER = int(env("BOUNDLESS_DEAD_ITEM_MULTIPLIER", default=1))
BOUNDLESS_EXO_SEARCH_RADIUS = 10
BOUNDLEXX_WORLD_SEARCH_OFFSET = timedelta(days=60)
BOUNDLESS_MAX_WORLD_ID = 5000
BOUNDLESS_MAX_SCAN_CHUNK = 50
BOUNDLESS_EXO_EXPIRED_BASE_ID = 2000000000
BOUNDLESS_FORUM_BAD_TOPICS = [
    28861,
    28592,
    28593,
    38617,
    50102,
    42678,
    50801,
    51538,
    50754,
    51356,
    51374,
    51239,
    51064,
]
BOUNDLESS_BLACKLISTED_ITEMS = [
    10649,  # dormant meteorite
    33102,  # coin
    11077,  # LED1
    11081,  # SPECIAL_BLINK_LED2
    11085,  # SPECIAL_BLINK_LED3
    11089,  # SPECIAL_BLINK_LED4
    11093,  # SPECIAL_BLINK_LED5
    11097,  # SPECIAL_BLINK_LED6
    11101,  # SPECIAL_BLINK_LED7
    11105,  # SPECIAL_BLINK_LED8
    11109,  # SPECIAL_BLINK_LED9
    11113,  # SPECIAL_BLINK_LED10
    11117,  # SPECIAL_BLINK_LED11
    11121,  # SPECIAL_BLINK_LED12
    11125,  # SPECIAL_BLINK_LED13
    11129,  # SPECIAL_BLINK_LED14
    11133,  # SPECIAL_BLINK_LED15
    11620,  # clay tilled
    11624,  # peaty tilled
    11628,  # silty tilled
    13560,  # marble frieze1
    13580,  # marble frieze2
    13600,  # marble frieze3
]
BOUNDLESS_NO_SELL = [
    13,  # verdant grass block item
    3085,  # barbed grass block item
    6157,  # gnarled grass block item
]
BOUNDLESS_TESTING_FEATURES = env.bool("BOUNDLESS_TESTING_FEATURES", default=False)
BOUNDLESS_FORUM_BASE_URL = env(
    "BOUNDLESS_FORUM_BASE_URL", default="https://forum.playboundless.com"
)
BOUNDLESS_FORUM_POST_USER = env("BOUNDLESS_FORUM_POST_USER", default="")
BOUNDLESS_FORUM_POST_KEY = env("BOUNDLESS_FORUM_POST_KEY", default="")
BOUNDLESS_FORUM_NAME_MAPPINGS = {
    "Ancient": "Ancient Wood Trunk",
    "Barbed": "Barbed Grass",
    "Branch Funnel": "Branch Funnel Fungus",
    "Clay": "Clay Soil",
    "Clustered Tongue": "Clustered Tongue Fungus",
    "Exotic": "Exotic Foliage",
    "Glow Cap": "Glow Cap Fungus",
    "Gnarled": "Gnarled Grass",
    "Igneous": "Igneous Rock",
    "Lush": "Lush Foliage",
    "Lustrous": "Lustrous Wood Trunk",
    "Metamorphic": "Metamorphic Rock",
    "Tar Spot": "Mottled Tar Spot Fungus",
    "Oortians Staff": "Oortian's Staff",
    "Peaty": "Peaty Soil",
    "Silty": "Silty Soil",
    "Sedimentary": "Sedimentary Rock",
    "Thorn": "Thorns",
    "Tinted-Burst": "Tinted-Burst Fungus",
    "Travellers Perch": "Traveller's Perch",
    "Verdant": "Verdant Grass",
    "Weeping Waxcap": "Weeping Waxcap Fungus",
}
BOUNDLESS_LANGUAGES = [
    ("english", "English"),
    ("french", "French"),
    ("german", "German"),
    ("italian", "Italian"),
    ("spanish", "Spanish"),
]
BOUNDLESS_WORLD_LIQUIDS = {
    "DEFAULT": ("Water", "Lava"),
    "LUSH": ("Water", "Water"),
    "METAL": ("Lava", "Lava"),
    "CHILL": ("Water", "Water"),
    "BURN": ("Lava", "Lava"),
    "DARKMATTER": ("Lava", "Water"),
}
BOUNDLESS_WORLD_TYPE_MAPPING = {
    1: "LUSH",
    2: "COAL",
    3: "METAL",
    4: "CORROSIVE",
    5: "BURN",
    6: "CHILL",
    7: "TOXIC",
    8: "SHOCK",
    9: "BLAST",
    10: "RIFT",
    11: "BLINK",
    12: "DARKMATTER",
}

BOUNDLESS_TRANSFORMATION_GROUPS = {
    10842: [10806],  # Ice
    10806: [10842],  # Glacier
    10798: [10794, 10802],  # Igneous Rock
    10794: [10798, 10802],  # Metamorphic Rock
    10802: [10798, 10794],  # Sedimentary Rock
    11588: [11592, 11584],  # Clay Soil
    11592: [11588, 11584],  # Peaty Soil
    11584: [11588, 11592],  # Silty Soil
    10814: [10798, 10794, 10802],  # Gravel
    10810: [10814, 10798, 10794, 10802],  # Sand
    10826: [10822, 10818],  # Waxy Foliage
    10822: [10826, 10818],  # Exotic Foliage
    10818: [10826, 10822],  # Lush Foliage
    10830: [10838, 10834],  # Ancient Wood Trunk
    10838: [10830, 10834],  # Lustrous Wood Trunk
    10834: [10830, 10838],  # Twisted Wood Trunk
    3085: [6157, 13],  # Barbed Grass
    6157: [3085, 13],  # Gnarled Grass
    13: [3085, 6157],  # Verdant Grass
}

BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING = [
    13620,  # Rough Amethyst
    13624,  # Rough Diamond
    13628,  # Rough Emerald
    13632,  # Rough Topaz
    13636,  # Rough Ruby
    13640,  # Rough Sapphire
    13644,  # Rough Rift
    13648,  # Rough Blink
    13652,  # Copper Ore
    13656,  # Iron Ore
    13660,  # Silver Ore
    13664,  # Gold Ore
    13668,  # Titanium Ore
    13672,  # Soft Coal
    13676,  # Medium Coal
    13680,  # Hard Coal
    13684,  # Small Fossil
    13688,  # Medium Fossil
    13692,  # Large Fossil
    13696,  # Ancient Tech Remnant
    13700,  # Ancient Tech Component
    13704,  # Ancient Tech Device
    13708,  # Rough Umbris
    13712,  # Rough Oortstone
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

BOUNDLESS_WORLD_POLL_GROUP_ORDER = {
    "": [9555],
    "rock": [10798, 10794, 10802],
    "wood": [10830, 10838, 10834],
    "foliage": [10822, 10818, 10826],
    "soil": [11588, 11592, 11584, 10846, 10850, 10814, 10810],
    "grass": [3085, 6157, 13],
    "misc": [10870, 10842, 10806, 10866, 10854, 10858, 10862],
    "flower": [9839, 9838, 9841, 9840],
    "plant": [10777, 10781, 10776, 10778, 10780, 10774, 10775, 10779],
    "fungus": [10790, 10789, 10793, 10788, 10791, 10792],
}

BOUNDLESS_WORLD_POLL_COLOR_GROUPINGS = {
    9555: "",  # Gleam
    10798: "rock",  # Igneous
    10794: "rock",  # Metamorhic
    10802: "rock",  # Sedimentary
    10830: "wood",  # Ancient Trunk
    10838: "wood",  # Lustrous Trunk
    10834: "wood",  # Twisted Trunk
    10822: "foliage",  # Exotic Leaves
    10818: "foliage",  # Lust Leaves
    10826: "foliage",  # Waxy Leaves
    11588: "soil",  # Clay Soil
    11592: "soil",  # Peaty Soil
    11584: "soil",  # Silty Soil
    10846: "soil",  # Mud
    10850: "soil",  # Ash
    10814: "soil",  # Gravel
    10810: "soil",  # Sand
    3085: "grass",  # Barbed Grass
    6157: "grass",  # Gnarled Grass
    13: "grass",  # Verdant Grass
    10870: "misc",  # Growth
    10842: "misc",  # Ice
    10806: "misc",  # Glacier
    10866: "misc",  # Mould
    10854: "misc",  # Sponge
    10858: "misc",  # Tangle
    10862: "misc",  # Thorns
    9838: "flower",  # Gladeflower
    9839: "flower",  # Cloneflower
    9840: "flower",  # Spineflower
    9841: "flower",  # Ghostflower
    10775: "plant",  # Trumpet Root
    10774: "plant",  # Traveller's Perch
    10779: "plant",  # Twisted Aloba
    10778: "plant",  # Spineback Planet
    10781: "plant",  # Oortian's Staff
    10776: "plant",  # Rosetta Nox
    10780: "plant",  # Stardrop Plant
    10777: "plant",  # Desert Sword
    10788: "fungus",  # Mottled Tar Spot Fungus
    10789: "fungus",  # Clustered Tongue Fungus
    10790: "fungus",  # Branch Funnel
    10792: "fungus",  # Weeping Waxcap
    10793: "fungus",  # Glow Cap
    10791: "fungus",  # Tinted-Burst
}

BOUNDLESS_BOWS = {
    "CORROSIVE": {
        "best": ["topaz"],
        "neutral": ["sapphire", "diamond"],
        "lucent": ["rift"],
    },
    "SHOCK": {
        "best": ["amethyst"],
        "neutral": ["emerald", "ruby"],
        "lucent": ["umbris"],
    },
    "BLAST": {
        "best": ["emerald"],
        "neutral": ["amethyst", "sapphire"],
        "lucent": ["umbris"],
    },
    "TOXIC": {"best": ["diamond"], "neutral": ["ruby", "topaz"], "lucent": ["blink"]},
    "CHILL": {
        "best": ["ruby"],
        "neutral": ["diamond", "amethyst"],
        "lucent": ["blink"],
    },
    "BURN": {"best": ["sapphire"], "neutral": ["emerald", "topaz"], "lucent": ["rift"]},
    "DARKMATTER": {
        "best": ["diamond", "topaz"],
        "neutral": [],
        "lucent": ["rift", "blink"],
    },
    "RIFT": {
        "best": ["ruby", "amethyst"],
        "neutral": [],
        "lucent": ["blink", "umbris"],
    },
    "BLINK": {
        "best": ["sapphire", "emerald"],
        "neutral": [],
        "lucent": ["rift", "umbris"],
    },
}

API_PROTOCOL = env("API_PROTOCOL", default="http")

STEAM_USERNAMES = env.list("STEAM_USERNAMES", default=[])
STEAM_PASSWORDS = env.list("STEAM_PASSWORDS", default=[])
STEAM_SENTRY_DIR = "/app/.steam"
STEAM_APP_ID = 324510
STEAM_AUTH_SCRIPT = "/usr/local/bin/steam-auth-ticket"
STEAM_AUTH_NODE_MODULES = "/usr/local/lib/node_modules"

ADMIN_DOMAIN_REPLACEMENTS = {
    "boundlexx.app": "boundlexx.wl.mort.is",
    "local.boundlexx.app": "local-boundlexx.wl.mort.is",
}


if BOUNDLESS_DS_REQUIRES_AUTH:
    if not (BOUNDLESS_PASSWORDS or STEAM_USERNAMES or STEAM_PASSWORDS):
        raise ValueError(
            "BOUNDLESS_PASSWORDS, STEAM_USERNAMES, and STEAM_PASSWORDS required "
            "if the Boundless DS server requires auth"
        )
