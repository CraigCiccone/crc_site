"""Contains database models for the application.

Example Usage::

    Initialize the database based on the current models.

    $ export FLASK_APP=run.py
    $ export FLASK_APP_ENV=Dev
    $ flask db init
    $ flask db migrate
    $ flask db upgrade

    Upgrade the database based on model changes.

    $ export FLASK_APP=run.py
    $ export FLASK_APP_ENV=Dev
    $ flask db migrate
    $ flask db upgrade
"""

from datetime import datetime
from typing import List

from flask_login import UserMixin

from app.extensions import db


#: Table mapping user roles to actual users
role_user_map = db.Table(
    "role_user_map",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class User(db.Model, UserMixin):
    """Database table storing user data."""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    pw_hash = db.Column(db.Binary(64), nullable=False)
    auth_fail = db.Column(db.Integer, default=0, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship(
        "Role",
        secondary=role_user_map,
        backref=db.backref("users", lazy="dynamic"),
    )

    def get_roles(self) -> List[str]:
        """Get all of the roles this user has.

        Returns:
            A list of the user's roles.
        """
        return [role.name for role in self.roles]


class Role(db.Model):
    """Database table storing possible user roles."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
