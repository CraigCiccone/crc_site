"""Utility functions for authentication."""

from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Dict, List, Union

from bcrypt import checkpw
from flask import abort, current_app as app, request, jsonify
from flask_login import current_user
from itsdangerous import BadSignature, BadTimeSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer

from app.extensions import db
from app.models.db import User
from app.utils.base import Return


def authenticate(email: str, pw: str) -> Return:
    """Checks the user's email and password to authenticate them.

    Args:
        email: The user's email address.
        pw: The user's password

    Returns:
        An object describing the status of the user's attempt.
    """
    user = db.session.query(User).filter(User.email == email.lower()).first()

    if not user:
        # This message is used to prevent attackers from guessing emails
        return Return(False, "Invalid email or password", user)
    elif user.auth_fail > app.config["AUTH_FAILS"]:
        app.logger.warning(f"{email} is locked out")
        return Return(
            False,
            "Your account is locked out. Please recover your account.",
            user,
        )
    elif checkpw(pw.encode("utf-8"), user.pw_hash):
        # Reset the user's authentication failure counter.
        user.auth_fail = 0
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"Successful login for : {email}")
        return Return(True, "Login Successful", user)
    else:
        # Increment the auth failure counter for an invalid password.
        user.auth_fail += 1
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"Failed login for : {email}")
        return Return(False, "Invalid email or password", user)


def generate_jwt(email: str, roles: List[str]) -> str:
    """Generates a java web token (JWT) for user authentication.

    Args:
        email: The user's email address.
        roles: A list of roles the user has.

    Returns:
        A java web token used to authenticate the user.
    """

    s = TimedJSONWebSignatureSerializer(
        secret_key=app.config["SECRET_KEY"],
        expires_in=app.config["JWT_EXP_SEC"],
    )
    jwt = s.dumps(
        {
            "exp": str(
                datetime.utcnow()
                + timedelta(seconds=app.config["JWT_EXP_SEC"])
            ),
            "iat": str(datetime.utcnow()),
            "sub": email,
            "roles": roles,
        }
    ).decode("utf-8")

    return jwt


def load_pw_token(token: str) -> Union[Dict, None]:
    """Tries to validate an expiring password reset token.

    Args:
        token: The token to decode.

    Returns:
        If successful, a decoded password reset token. Otherwise, None.
    """

    try:
        s = TimedJSONWebSignatureSerializer(app.config["SECRET_KEY"])
        return s.loads(token.encode("utf-8"))
    except (SignatureExpired, BadTimeSignature, BadSignature):
        return None


def required_roles_ui(*roles: str) -> Callable:
    """Decorator function to check if a user has the required UI roles.

    Args:
        *roles: Variable length argument list of user roles.

    Returns:
        The decorated function if authorized, otherwise an error.
    """

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Store whether or not the user is authenticated
            authenticated = current_user.is_authenticated

            # Check for an authenticated user with the proper roles
            if authenticated and set(roles).issubset(current_user.get_roles()):
                return f(*args, **kwargs)

            # Abort at this point as the user is not authorized
            abort(401)

        return wrapped

    return wrapper


def required_roles_api(*roles: str) -> Callable:
    """Decorator function to check if a user has the required api roles.

    Args:
        *roles: Variable length argument list of user roles.

    Returns:
        The decorated function if authorized, otherwise an error.
    """

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            # Store the authorization header
            header = request.headers.get("Authorization")

            # Check if the header contains a valid token
            if header and "Bearer" in header:

                # Parse the token from the header
                token = header.split("Bearer ")[1]
                token_data = validate_jwt(token)

                # Validate the user's roles
                if token_data and set(roles).issubset(token_data["roles"]):
                    return f(*args, **kwargs)

            # Abort the API at this point as the user is not authorized
            response = jsonify(
                {"status": "failure", "message": "Unauthorized"}
            )
            response.status_code = 401
            abort(response)

        return wrapped

    return wrapper


def serialize_pw_token(email: str) -> str:
    """Generates an expiring password reset token for a user.

    The token is provided to the user via email embedded in a URL. The
    URL will allow the user to reset their password as long as the token
    has not expired.

    Args:
        email: The user's email.

    Returns:
        A password token mapped to the user's email.
    """

    s = TimedJSONWebSignatureSerializer(
        app.config["SECRET_KEY"], app.config["PW_TOKEN_EXP_SEC"]
    )
    return s.dumps({"email": email}).decode("utf-8")


def validate_jwt(token: str) -> Union[Dict, None]:
    """Try to validate a java web token.

    Args:
        token: The token to decode.

    Returns:
        If successful, a decoded JWT. Otherwise, None.
    """
    try:
        s = TimedJSONWebSignatureSerializer(app.config["SECRET_KEY"])
        return s.loads(token.encode("utf-8"))
    except (SignatureExpired, BadTimeSignature, BadSignature):
        return None
