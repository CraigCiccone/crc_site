"""Configuration information for the application.

The default config is the production configuration. Other configurations
can override the default via the FLASK_APP_ENV environment variable -
see run.py.
"""

import logging
from typing import Dict

from base64 import b64decode
from os import environ
from os.path import abspath, dirname, join
from typing import List


class Prod:
    """Production (default) configuration parameters."""

    # Authentication parameters
    AUTH_FAILS = 10

    # Celery parameters
    CELERY_BROKER_URL: str = "redis://redis:6379"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379"
    CELERY_INCLUDE: List[str] = ["app.tasks"]

    # Email parameters
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USERNAME: str = b64decode(environ.get("MAIL_USER")).decode("utf-8")
    MAIL_PASSWORD: str = b64decode(environ.get("MAIL_AUTH")).decode("utf-8")
    MAIL_TO: str = b64decode(environ.get("MAIL_TO")).decode("utf-8")

    # Flask debugging
    DEBUG: bool = False

    # Flask secret key
    SECRET_KEY: str = b64decode(environ.get("SECRET_KEY")).decode("utf-8")

    # General parameters
    DOMAIN = "CraigCiccone.com"

    # Logging parameters
    LOG_LEVEL = logging.INFO
    log_format_p1 = "[%(asctime)s] [%(levelname)8s] - %(message)s "
    log_format_p2 = "(%(funcName)s@%(pathname)s:%(lineno)d) [PID:%(process)d]"
    LOG_FORMAT = log_format_p1 + log_format_p2

    # Recaptcha parameters
    RECAPTCHA_PUBLIC_KEY: str = b64decode(environ.get("RECAP_PUBLIC")).decode(
        "utf-8"
    )
    RECAPTCHA_PRIVATE_KEY: str = b64decode(environ.get("RECAP_SECRET")).decode(
        "utf-8"
    )
    RECAPTCHA_DATA_ATTRS: Dict = {
        "theme": "dark",
        "bind": "submit_recap",
        "callback": "onSubmitCallback",
        "size": "invisible",
    }

    # SQLAlchemy parameters
    DB_UN: str = b64decode(environ.get("DB_UN")).decode("utf-8")
    DB_PW: str = b64decode(environ.get("DB_PW")).decode("utf-8")
    DB_NAME: str = b64decode(environ.get("DB_NAME")).decode("utf-8")
    DB_HOST: str = "mariadb"
    db_string: str = f"mysql+pymysql://{DB_UN}:{DB_PW}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI: str = db_string
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_RECORD_QUERIES: bool = False
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_POOL_TIMEOUT: int = 10
    SQLALCHEMY_POOL_RECYCLE: int = 550
    SQLALCHEMY_MAX_OVERFLOW: int = 2
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Token parameters
    JWT_EXP_SEC = 600
    PW_TOKEN_EXP_SEC = 3600


class Dev(Prod):
    """Override configuration parameters for development."""

    # Authentication parameters
    AUTH_FAILS = 3

    # Celery parameters
    CELERY_BROKER_URL = None
    CELERY_ALWAYS_EAGER: bool = True
    CELERY_RESULT_BACKEND: str = "cache"
    CELERY_CACHE_BACKEND: str = "memory"
    CELERY_TASK_EAGER_PROPAGATES: bool = True

    # Directory parameters
    BASE_DIR: str = abspath(join(dirname(__file__)))

    # Flask debugging
    DEBUG: bool = True

    # General parameters
    DOMAIN = "localhost:5000"

    # Logging parameters
    LOG_LEVEL = logging.DEBUG

    # SQLAlchemy parameters
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{BASE_DIR}/dev_db.db"
    SQLALCHEMY_POOL_SIZE = None
    SQLALCHEMY_POOL_TIMEOUT = None
    SQLALCHEMY_MAX_OVERFLOW = None

    # Token parameters
    JWT_EXP_SEC: int = 120
    PW_TOKEN_EXP_SEC: int = 60


class Test(Prod):
    """Override configuration parameters for testing."""

    # Celery parameters
    CELERY_BROKER_URL = None
    CELERY_ALWAYS_EAGER: bool = True
    CELERY_RESULT_BACKEND: str = "cache"
    CELERY_CACHE_BACKEND: str = "memory"
    CELERY_TASK_EAGER_PROPAGATES: bool = True

    # CSRF parameters
    WTF_CSRF_ENABLED = False

    # Directory parameters
    BASE_DIR: str = abspath(join(dirname(__file__)))

    # Flask debugging
    DEBUG: bool = True

    # Mail parameters
    TESTING = True
    MAIL_USERNAME = "test"
    MAIL_TO = "test@test.com"

    # Recaptcha parameters
    # Test keys: https://developers.google.com/recaptcha/docs/faq
    RECAPTCHA_PUBLIC_KEY: str = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
    RECAPTCHA_PRIVATE_KEY: str = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

    # SQLAlchemy parameters
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{BASE_DIR}/test_db.db"
    SQLALCHEMY_POOL_SIZE = None
    SQLALCHEMY_POOL_TIMEOUT = None
    SQLALCHEMY_MAX_OVERFLOW = None
