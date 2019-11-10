"""Functions to create and configure the Flask application are defined here."""

from importlib import import_module

from flask import Flask, request, render_template

from app.blueprints import blueprints
from config import Prod


def create_app(config=None, path="config"):
    """
    Create a Flask application object using the Application Factory pattern.

    Args:
        config (str): Any config class used to override the default production
            configuration. See config.py for available configurations.
        path (str): The path to the file that contains the config classes.

    Returns:
        app: A fully configured and runnable Flask application object.
    """

    # Create the Flask application object
    app = Flask(__name__)

    # Apply the default (production) configurations
    app.config.from_object(Prod)

    # Override the configurations if necessary
    if config:
        app.config.from_object(obj=f"{path}.{config}")

    # Import all views and register all Blueprints
    for blueprint in blueprints:
        import_module(blueprint.import_name)
        app.register_blueprint(blueprint)

    return app
