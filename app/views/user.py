"""Application views that handle general user management."""

from bcrypt import checkpw, gensalt, hashpw
from flask import current_app as app, flash, redirect, request, render_template
from flask import url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints import user
from app.extensions import db
from app.forms import PasswordForm, LoginForm, RecoverForm, RegisterForm
from app.models.db import Role, User
from app.utils.auth import authenticate, load_pw_token, serialize_pw_token
from app.utils.user import change_pw
from app.tasks import send_new_user_email, send_recovery_email


@user.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Allows an authenticated user to delete their account."""

    # Initialize the form and heading text.
    form = PasswordForm()
    heading = "Delete Account"

    # If the form is valid, try to delete the user.
    if form.validate_on_submit():

        u = (
            db.session.query(User)
            .filter(User.email == current_user.email)
            .first()
        )

        # Delete the user if they provided the proper password.
        if u and checkpw(form.pw.data.encode("utf-8"), u.pw_hash):
            logout_user()
            db.session.delete(u)
            db.session.commit()
            flash(
                f'Your account, "{u.email}", has been removed',
                category="secondary",
            )
            app.logger.info(f"Removed account : {u.email}")
            return redirect(url_for("base.index"))
        else:
            flash("Invalid Password", category="danger")
            app.logger.warning(f"Attempted account removal: {u.email}")

    return render_template("user/form.html", form=form, heading=heading)


@user.route("/login", methods=["GET", "POST"])
def login():
    """Allows a registered user to log into the application."""

    # Redirect users who have already logged in
    if current_user.is_authenticated:
        return redirect(url_for("base.index"))

    # Initialize the form and heading text.
    form = LoginForm()
    heading = "Please Sign In"

    # Try to log the user in if the form is valid
    if form.validate_on_submit():

        # Authenticate the user via a function
        result = authenticate(form.email.data, form.pw.data)

        # Check the user's authentication status
        if result.success:
            # Log the user into the application
            login_user(result.data, remember=form.remember.data)
            flash(result.message, category="secondary")
            return redirect(url_for("base.index"))
        else:
            flash(result.message, category="danger")

    return render_template("user/form.html", form=form, heading=heading)


@user.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logs the user out of the application."""
    app.logger.info(f"Successful logout for : {current_user.email}")
    logout_user()
    flash("Logged out successfully", category="secondary")
    return redirect(url_for("base.index"))


@user.route("/recover", methods=["GET", "POST"])
def recover():
    """Allows the user to recover a forgotten account password."""

    # Initialize the form and the heading text.
    form = RecoverForm()
    heading = "Account Recovery"

    # If the form is valid, send the user an email to recover their password
    if form.validate_on_submit():

        u = (
            db.session.query(User)
            .filter(User.email == form.email.data.lower())
            .first()
        )

        if u:
            send_recovery_email.delay(
                form.email.data, serialize_pw_token(form.email.data)
            )
            flash(
                "Account recovery email sent successfully",
                category="secondary",
            )
            app.logger.info(
                f"Account recovery email sent to: {form.email.data}"
            )
            return redirect(url_for("user.login"))
        else:
            flash(
                f'No account exists for "{form.email.data}", please register',
                category="danger",
            )
            app.logger.warning(
                f"Cannot recover unregistered email : {form.email.data}"
            )
            return redirect(url_for("user.register"))

    return render_template("user/form.html", form=form, heading=heading,)


@user.route("/register", methods=["GET", "POST"])
def register():
    """Allows the user to register a new account."""

    # Initialize the form and the heading text.
    form = RegisterForm()
    heading = "Register Account"

    # If the form is valid, try to register the user.
    if form.validate_on_submit():

        # Query for the new user by their email.
        new_user = (
            db.session.query(User)
            .filter(User.email == form.email.data.lower())
            .first()
        )

        # Add the user if they don't already exist.
        if new_user:
            flash(
                f'"{form.email.data}" account already exists',
                category="danger",
            )
            app.logger.warning(
                f'Attempt to register existing : "{form.email.data}" from "'
                f'{request.environ["REMOTE_ADDR"]}'
            )
            return redirect(url_for("user.login"))
        else:
            # noinspection PyArgumentList
            new_user = User(
                email=form.email.data.lower(),
                pw_hash=hashpw(form.pw.data.encode("utf-8"), gensalt()),
            )
            new_user.roles.append(Role.query.filter_by(name="user").first())
            db.session.add(new_user)
            db.session.commit()
            send_new_user_email.delay(form.email.data)
            app.logger.info(
                f'Successful account registration : {form.email.data} from "'
                f'"{request.environ["REMOTE_ADDR"]}'
            )
            flash("Account registration successful", category="secondary")
            return redirect(url_for("user.login"))

    return render_template("user/form.html", form=form, heading=heading)


@user.route("/reset", methods=["GET", "POST"])
def reset():
    """Allows the user to reset their password.

    This is secured using an expiring token which is sent to the user
    via email. This endpoint will redirect the user elsewhere if the
    token is missing, invalid, or expired.
    """

    # Redirect users who are already logged in.
    if current_user.is_authenticated:
        flash("You are already logged in", category="danger")
        app.logger.info(
            f'Attempted reset from logged in user : {current_user.email} from"'
            f' {request.environ["REMOTE_ADDR"]}'
        )
        return redirect(url_for("base.index"))

    # Get the token from the URL.
    token = request.args.get("token", None)

    # Ensure a token is provided.
    if not token:
        app.logger.warning(
            f'No token sent to the "reset" page from "'
            f'{request.environ["REMOTE_ADDR"]}'
        )
        flash("Your request is not valid", category="danger")
        return redirect(url_for("base.index"))

    # Ensure the provided token is valid
    token_data = load_pw_token(token)

    if token_data:

        # Store the user's email
        email = token_data["email"].lower()

        # Initialize the form and the heading text.
        form = PasswordForm()
        heading = "Reset Password"

        # If the form is valid, reset the user's password.
        if form.validate_on_submit():
            result = change_pw(email, form.pw.data)
            if result.success:
                flash(
                    result.message, category="secondary",
                )
                return redirect(url_for("user.login"))
            else:
                flash(result.message)
                return redirect(url_for("user.register"))

        return render_template("user/form.html", form=form, heading=heading)

    else:
        app.logger.warning(
            f'Invalid token passed to the "reset" page from "'
            f'{request.environ["REMOTE_ADDR"]}'
        )
        flash("Your request is no longer valid", category="danger")
        return redirect(url_for("user.recover"))
