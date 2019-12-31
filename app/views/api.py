"""API views supported by the application."""

from flask import jsonify, request
from pydantic import ValidationError

from app.blueprints import api
from app.extensions import db
from app.models.api import AccountReq, AuthReq, AuthResp, BaseResp, MessageReq
from app.models.db import User
from app.tasks import send_contact_email
from app.utils.auth import (
    authenticate,
    generate_jwt,
    required_roles_api,
    validate_jwt,
)
from app.utils.user import change_pw


@api.route("/api/account", methods=["PUT"])
@required_roles_api(*["user"])
def change_password():
    """Changes the password for a user's account."""

    # Validate the request data
    try:
        req = AccountReq(**request.json)
    except ValidationError as e:
        return e.json(), 400

    # Load the token
    header = request.headers.get("Authorization")
    jwt = header.split("Bearer ")[1]
    token_data = validate_jwt(jwt)

    # Change the password via a function
    result = change_pw(token_data["sub"], req.password)

    # Return the results of the password change
    if result.success:
        return jsonify(
            BaseResp(status="success", message=result.message).dict()
        )
    else:
        return jsonify(
            BaseResp(status="failure", message=result.message).dict(), 400
        )


@api.route("/api/account", methods=["DELETE"])
@required_roles_api(*["user"])
def delete_account():
    """Deletes a user's account."""

    # Load the token
    header = request.headers.get("Authorization")
    jwt = header.split("Bearer ")[1]
    token_data = validate_jwt(jwt)

    # Delete the user
    user = (
        db.session.query(User).filter(User.email == token_data["sub"]).first()
    )
    db.session.delete(user)
    db.session.commit()

    # Return the results of the account deletion
    return jsonify(
        BaseResp(
            status="success", message="Account deleted successfully"
        ).dict()
    )


@api.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint that returns a simple JSON payload."""
    return jsonify({"status": "online"})


@api.route("/api/message", methods=["POST"])
@required_roles_api(*["user"])
def message():
    """Sends a message to the website owner."""

    # Validate the request data
    try:
        req = MessageReq(**request.json)
    except ValidationError as e:
        return e.json(), 400

    # Load the token
    header = request.headers.get("Authorization")
    jwt = header.split("Bearer ")[1]
    token_data = validate_jwt(jwt)

    # Send the contact message
    send_contact_email.delay(
        req.first, req.last, req.message, token_data["sub"], req.category,
    )

    # Default return value for failed authentication
    return jsonify(
        BaseResp(status="success", message="Message sent successfully").dict()
    )


@api.route("/api/token", methods=["POST"])
def token():
    """Generates a token to used to access protected APIs."""

    # Validate the request data
    try:
        req = AuthReq(**request.json)
    except ValidationError as e:
        return e.json(), 400

    # Authenticate the user
    result = authenticate(req.email, req.password)

    # Return the JWT if the authentication was successful
    if result.success:
        jwt = generate_jwt(req.email, result.data.get_roles())
        return jsonify(
            AuthResp(
                status="success",
                message="Token generated successfully",
                token=jwt,
            ).dict()
        )

    # Default return value for failed authentication
    return (
        jsonify(BaseResp(status="failure", message=result.message).dict()),
        401,
    )
