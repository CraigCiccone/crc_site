"""
Configuration information for the application. DefaultConfig is the production
configuration. Other configurations can override the default via run.py.
"""

from base64 import b64decode
from os import environ


class Prod:
    """Production (default) configuration parameters."""

    # Flask debugging
    DEBUG = False

    # Flask secret key
    SECRET_KEY = b64decode(environ.get('SECRET_KEY')).decode('utf-8')


class Dev:
    """Override configuration parameters for development."""

    # Flask debugging
    DEBUG = True


class Test:
    """Override configuration parameters for testing."""

    # Flask debugging
    DEBUG = True
