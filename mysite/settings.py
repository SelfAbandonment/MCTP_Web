"""
mysite 项目的 Django 设置。

由 django-admin startproject 生成（Django 5.2.7），此文件根据环境变量与 .env 进行配置，支持开发/生产切换。
"""

from pathlib import Path
import os
import importlib
_util = getattr(importlib, 'util', None)
_DOTENV_AVAILABLE = _util.find_spec("dotenv") is not None if _util else False
if _DOTENV_AVAILABLE:
    dotenv_module = importlib.import_module("dotenv")
else:
    dotenv_module = None

BASE_DIR = Path(__file__).resolve().parent.parent

# 在项目根目录加载 .env
ENV_FILE = BASE_DIR / ".env"
if dotenv_module and ENV_FILE.exists():
    dotenv_module.load_dotenv(ENV_FILE)

# ----------------------------------------
# 环境开关
# ----------------------------------------
DJANGO_ENV = os.getenv("DJANGO_ENV", "development").lower()
DEBUG = os.getenv("DEBUG", "true" if DJANGO_ENV == "development" else "false").lower() in {"1", "true", "yes", "on"}

# 生产环境务必替换 SECRET_KEY
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-please-change-this-in-production",
)

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# ----------------------------------------
# 应用注册
# ----------------------------------------
INSTALLED_APPS = [
    # 后台界面
    "simpleui",
    # Django 内置
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 第三方应用
    "ckeditor",
    "ckeditor_uploader",
    "django_extensions",
    "django_cleanup.apps.CleanupConfig" if os.getenv("ENABLE_DJANGO_CLEANUP", "1") in {"1","true","yes"} else None,
]
# 过滤掉可能的 None
INSTALLED_APPS = [app for app in INSTALLED_APPS if app]

# 本地应用
INSTALLED_APPS += [
    "common",
    "players",
    "api",
]

# 仅在开发环境启用调试工具栏
if DJANGO_ENV == "development":
    INSTALLED_APPS += ["debug_toolbar"]

# ----------------------------------------
# 中间件
# ----------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DJANGO_ENV == "development":
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# 挂载统一 API 异常处理与安全响应头
MIDDLEWARE += [
    "common.api_middleware.ApiExceptionMiddleware",
    "mysite.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "mysite.urls"

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

WSGI_APPLICATION = "mysite.wsgi.application"
ASGI_APPLICATION = "mysite.asgi.application"

# ----------------------------------------
# 数据库
# ----------------------------------------
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
if DB_ENGINE in {"sqlite", "sqlite3"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / os.getenv("DB_NAME", "db.sqlite3")),
        }
    }
elif DB_ENGINE in {"postgres", "postgresql", "psql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "mctp"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }
elif DB_ENGINE in {"mysql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "mctp"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    raise RuntimeError(f"不支持的 DB_ENGINE: {DB_ENGINE}")

# ----------------------------------------
# 认证 / 用户
# ----------------------------------------
AUTH_USER_MODEL = "players.User"
AUTHENTICATION_BACKENDS = [
    "players.auth_backends.UsernameOrQQBackend",  # 支持用户名或 QQ 号登录
    "django.contrib.auth.backends.ModelBackend",
]

# 密码校验（包含复杂度校验器）
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "common.validators.ComplexityPasswordValidator", "OPTIONS": {"min_upper": 1, "min_lower": 1, "min_digits": 1, "min_symbols": 1}},
]

LOGIN_URL = os.getenv("LOGIN_URL", "/admin/login/")
LOGIN_REDIRECT_URL = os.getenv("LOGIN_REDIRECT_URL", "/")
LOGOUT_REDIRECT_URL = os.getenv("LOGOUT_REDIRECT_URL", "/")

# 登录失败限制（次数与锁定分钟）
LOGIN_ATTEMPT_LIMIT = int(os.getenv("LOGIN_ATTEMPT_LIMIT", "5"))
LOGIN_LOCKOUT_MINUTES = int(os.getenv("LOGIN_LOCKOUT_MINUTES", "15"))

# ----------------------------------------
# 国际化
# ----------------------------------------
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "zh-hans")
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Shanghai")
USE_I18N = True
USE_TZ = True

# ----------------------------------------
# 静态与媒体
# ----------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / os.getenv("STATIC_ROOT", "static")
STATICFILES_DIRS = [p for p in [BASE_DIR / "assets"] if p.exists()]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / os.getenv("MEDIA_ROOT", "media")

# 媒体上传限制（尺寸/格式），供校验器使用
MEDIA_MAX_IMAGE_SIZE_MB = int(os.getenv("MEDIA_MAX_IMAGE_SIZE_MB", "5"))
ALLOWED_IMAGE_FORMATS = os.getenv("ALLOWED_IMAGE_FORMATS", "JPEG,PNG,WEBP").split(",")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------
# 缓存
# ----------------------------------------
if DJANGO_ENV == "production" and os.getenv("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": os.getenv("REDIS_PASSWORD", None),
            },
            "KEY_PREFIX": os.getenv("CACHE_KEY_PREFIX", "mctp"),
            "TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300")),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "mctp-local",
            "TIMEOUT": 300,
        }
    }

# ----------------------------------------
# 日志
# ----------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s %(module)s:%(lineno)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DJANGO_ENV != "development" else "simple",
        },
    },
    "loggers": {},
}

# 根据环境添加文件处理器（生产环境使用滚动日志）
if DJANGO_ENV == "production":
    LOGGING["handlers"]["app_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(LOG_DIR / "app.log"),
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 5,
        "formatter": "verbose",
        "encoding": "utf-8",
    }
    LOGGING["handlers"]["error_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(LOG_DIR / "error.log"),
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 10,
        "formatter": "verbose",
        "encoding": "utf-8",
    }
else:
    LOGGING["handlers"]["app_file"] = {
        "class": "logging.FileHandler",
        "filename": str(LOG_DIR / "app.log"),
        "formatter": "verbose",
        "encoding": "utf-8",
    }
    LOGGING["handlers"]["error_file"] = {
        "class": "logging.FileHandler",
        "filename": str(LOG_DIR / "error.log"),
        "formatter": "verbose",
        "encoding": "utf-8",
    }

LOGGING["loggers"] = {
    "django": {"handlers": ["console", "app_file"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"), "propagate": True},
    "django.request": {"handlers": ["error_file"], "level": "ERROR", "propagate": False},
    "app": {"handlers": ["app_file"], "level": "INFO", "propagate": False},
}

# ----------------------------------------
# 安全
# ----------------------------------------
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0" if DJANGO_ENV != "production" else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "1" if DJANGO_ENV == "production" else "0") in {"1","true","yes"}
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "1" if DJANGO_ENV == "production" else "0") in {"1","true","yes"}
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1" if DJANGO_ENV == "production" else "0") in {"1","true","yes"}
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "1" if DJANGO_ENV == "production" else "0") in {"1","true","yes"}
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# ----------------------------------------
# SimpleUI 配置
# ----------------------------------------
SIMPLEUI_CONFIG = {
    "system_keep": True,
    "menu_display": [],
    "dynamic": False,
    "home_info": [
        {"title": "MCTP 控制台", "content": "欢迎使用后台管理"},
    ],
}
SIMPLEUI_HOME_TITLE = os.getenv("SIMPLEUI_HOME_TITLE", "MCTP 管理后台")
SIMPLEUI_LOGIN_TITLE = os.getenv("SIMPLEUI_LOGIN_TITLE", "MCTP 管理登录")

# ----------------------------------------
# CKEditor 配置
# ----------------------------------------
CKEDITOR_UPLOAD_PATH = os.getenv("CKEDITOR_UPLOAD_PATH", "uploads/ckeditor/%Y/%m/")
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline", "RemoveFormat"],
            ["NumberedList", "BulletedList", "Blockquote"],
            ["Link", "Unlink", "Image", "Table"],
            ["Source", "Maximize"],
        ],
        "height": 300,
        "width": "100%",
        "removePlugins": "exportpdf,flash,forms",
        "extraAllowedContent": "img[!src,alt,width,height]",
        "filebrowserUploadUrl": "/ckeditor/upload/",
        "filebrowserBrowseUrl": "/ckeditor/browse/",
        "image_prefillDimensions": False,
    }
}

# ----------------------------------------
# 调试工具
# ----------------------------------------
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# ----------------------------------------
# Celery（占位）
# ----------------------------------------
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "1" if DJANGO_ENV == "development" else "0") in {"1","true","yes"}