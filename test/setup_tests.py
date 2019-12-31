"""Shared utilities for unit test cases."""

from unittest import TestCase

from bcrypt import hashpw, gensalt

from app.create import create_app
from app.extensions import db
from app.models.db import Role, User

# Global testing parameters
USR = "usr@usr.com"
ADM = "adm@adm.com"


class SetupTest(TestCase):
    """Prepare and clean up data required to run the unit tests."""

    def setUp(self):
        self.app = create_app("Test")
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            usr_role = Role(name="user")
            adm_role = Role(name="admin")
            db.session.add(usr_role)
            db.session.add(adm_role)
            # noinspection PyArgumentList
            db.session.add(
                User(
                    email=USR,
                    pw_hash=hashpw("password".encode("utf-8"), gensalt()),
                    roles=[usr_role],
                )
            )
            # noinspection PyArgumentList
            db.session.add(
                User(
                    email=ADM,
                    pw_hash=hashpw("password".encode("utf-8"), gensalt()),
                    roles=[adm_role, usr_role],
                )
            )
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()


def force_anon_user(app):
    """EditFlask-Login's request loader to force an anonymous user."""

    @app.login_manager.request_loader
    def load_user_from_request(_request):
        return None


def force_auth_user(app, admin=False):
    """EditFlask-Login's request loader to force a logged in user."""

    user = User.query.filter(User.email == str(ADM if admin else USR)).first()

    @app.login_manager.request_loader
    def load_user_from_request(_request):
        return user
