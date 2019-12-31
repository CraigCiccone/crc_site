"""Starts the Flask application.

It can be run in various configurations using the FLASK_APP_ENV
environment variable. The available configurations are defined in
conf/config.py.

Example Usage::
    $ export FLASK_APP=run.py
    $ export FLASK_APP_ENV=Dev
    $ flask run
"""

from os import environ

from app.create import create_app
from app.extensions import make_celery

app = create_app(config=environ.get("FLASK_APP_ENV", None))
celery = make_celery(app)

if __name__ == "__main__":
    app.run()
