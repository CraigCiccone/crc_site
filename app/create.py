"""Functions to create and configure the Flask application."""

from importlib import import_module
from logging.config import dictConfig

from flask import Flask, render_template, request
from flask_login import LoginManager

# noinspection PyProtectedMember
from flask_wtf.csrf import CSRFError

from app.blueprints import blueprints
from app.extensions import init_extensions, lm
from app.models.db import User
from config import Prod


def configure_logger(conf: str = None):
    """Configure logging to stdout.

    Args:
        conf: The configuration object to get the logging data from.
    """

    # Use the logging parameters from the corresponding config
    config = import_module("config")
    if not conf:
        conf = "Prod"

    # Configure the logger using a dictionary based configuration
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {"format": config.__dict__[conf].LOG_FORMAT}
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {
                "level": config.__dict__[conf].LOG_LEVEL,
                "handlers": ["wsgi"],
            },
        }
    )


def create_app(config: str = None, path: str = "config") -> Flask:
    """Creates a Flask object using the Application Factory pattern.

    Args:
        config: Any config class used to override the default production
            configuration. See config.py for available configurations.
        path: Path to the file that contains the config classes.

    Returns:
        A fully configured and runnable Flask application object.
    """

    # Set the application logger
    configure_logger(config)

    # Create the Flask application object
    app = Flask(__name__)

    # Apply the default (production) configurations
    app.config.from_object(Prod)

    # Override the config if necessary. Otherwise apply the default.
    if config:
        app.config.from_object(obj=f"{path}.{config}")

    # Configure Flask-Login's login manager
    set_user_loader(lm)

    # Initialize all extensions
    init_extensions(app)

    # Set the applications error handlers
    set_error_handlers(app)

    # Import all views and register all Blueprints
    for blueprint in blueprints:
        import_module(blueprint.import_name)
        app.register_blueprint(blueprint)

    return app


def set_error_handlers(app: Flask):
    """Configure front end error handlers.

    Note that all error handlers return an error template HTML page.

    Args:
        app: The Flask application object.
    """

    @app.errorhandler(401)
    def unauthorized_error(error):
        """HTTP error handler for 401 errors."""

        err_req = "Unauthorized"
        err_opt = "You are not authorized to access the URL requested"
        return (
            render_template(
                "base/error.html", err_req=err_req, err_opt=err_opt
            ),
            401,
        )

    @app.errorhandler(404)
    def not_found_error(error):
        """HTTP error handler for 404 errors."""

        err_req = "File Not Found"
        err_opt = "The requested resource was not found"
        return (
            render_template(
                "base/error.html", err_req=err_req, err_opt=err_opt
            ),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        """HTTP error handler for 405 errors."""

        err_req = "Method Not Allowed"
        err_opt = "The method is not allowed for the requested URL."
        return (
            render_template(
                "base/error.html", err_req=err_req, err_opt=err_opt
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """HTTP error handler for 500 errors."""

        app.logger.critical(
            "500 Internal Server Error ({ip:s}) : {desc}".format(
                desc=error, ip=request.environ["REMOTE_ADDR"]
            )
        )

        err_req = "An unexpected error has occurred"
        err_opt = "We apologize for the inconvenience"

        return (
            render_template(
                "base/error.html", err_req=err_req, err_opt=err_opt
            ),
            500,
        )

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        """CSRF error handler."""

        app.logger.warning(
            "CSRF Error ({ip:s}) : {desc:s}".format(
                ip=request.environ["REMOTE_ADDR"], desc=str(error)
            )
        )
        err_req = "Error"
        err_opt = "Your request could not be processed"
        return (
            render_template(
                "base/error.html", err_req=err_req, err_opt=err_opt
            ),
            400,
        )


def set_user_loader(login_manager: LoginManager):
    """Establish the user_loader call back for Flask-Login.

    Args:
        login_manager: The Flask-Login manager object.
    """

    def load_user(user_id):
        return User.query.get(user_id)

    login_manager.user_loader(load_user)
    login_manager.login_view = "user.login"
    login_manager.login_message_category = "danger"
