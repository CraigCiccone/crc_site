"""Declaration and initialization of all Flask extensions."""

from celery import Celery
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

#: Flask-CeleryExt object
celery = None

#: Flask-WTF CSRF Protect object
csrf: CSRFProtect = CSRFProtect()

#: Flask-SQLAlchemy DB object
db: SQLAlchemy = SQLAlchemy()

#: Flask-Login object
lm: LoginManager = LoginManager()

#: Flask-Mail object
mail: Mail = Mail()

#: Flask-Migrate object
migrate = Migrate()


def init_extensions(app: Flask):
    """Initialize all flask extensions.

    Args:
        app: The Flask application object.
    """

    global celery
    celery = make_celery(app)
    csrf.init_app(app)
    db.init_app(app)
    lm.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)


def make_celery(app: Flask):
    """Flask's recommended way to integrate Celery.

    Args:
        app: The Flask application object.
    """

    c = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    c.conf.update(app.config)

    class ContextTask(c.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # noinspection PyPropertyAccess
    c.Task = ContextTask
    return c
