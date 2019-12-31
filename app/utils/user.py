"""Utility functions for user management."""

from bcrypt import hashpw, gensalt
from flask import current_app as app

from app.extensions import db
from app.models.db import User
from app.utils.base import Return


def change_pw(email: str, pw: str) -> Return:
    """Change the user's password.

    Args:
        email: The email of the user.
        pw: The new password for the user.

    Returns:
        An object describing the status of the password change.
    """
    user = db.session.query(User).filter(User.email == email).first()
    if user:
        user.pw_hash = hashpw(pw.encode("utf-8"), gensalt())
        user.auth_fail = 0
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"Password reset completed by : {email}")
        return Return(
            True, "Your password has been updated successfully", user
        )
    else:
        return Return(False, f'"{email}" is not registered', user)
