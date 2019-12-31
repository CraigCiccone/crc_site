"""Asynchronous Celery tasks."""

from flask import current_app as app, render_template
from flask_mail import Message

from app.extensions import celery, mail


@celery.task()
def send_contact_email(
    first: str,
    last: str,
    message: str,
    email: str = None,
    category: str = None,
):
    """Emails a message submitted by a user to the website owner.

    Args:
        first: The user's first name.
        last: The user's last name.
        message: The message content from the user.
        email: The user's email address.
        category: A high level category classifying the email message.
    """
    msg = Message(
        f"CRC User Message : {first} {last}",
        sender=email if email else "unknown",
        recipients=[app.config["MAIL_TO"]],
    )
    msg.body = render_template(
        "email/contact.txt",
        first=first,
        last=last,
        message=message,
        email=email,
        category=category,
    )
    msg.html = render_template(
        "email/contact.html",
        first=first,
        last=last,
        message=message,
        email=email,
        category=category,
    )
    mail.send(msg)


@celery.task()
def send_new_user_email(email: str):
    """Welcome new users with an email.

    This also notifies the website admin of the new user registration
    via email.

    Args:
        email: The email address to send the email to.
    """

    # The base URL to log into the site.
    site_url = f"http://{app.config['DOMAIN']}/login"

    msg = Message("CRC Welcome", sender="CRC Site", recipients=[email])
    msg.body = render_template(
        "email/new_user.txt", email=email, site_url=site_url
    )
    msg.html = render_template(
        "email/new_user.html", email=email, site_url=site_url
    )

    adm_msg = Message(
        "CRC New User", sender="CRC Site", recipients=[app.config["MAIL_TO"]]
    )
    adm_msg.body = email

    mail.send(msg)
    mail.send(adm_msg)


@celery.task()
def send_recovery_email(email: str, token: str):
    """Email the user a link to recover their password

    Args:
        email: The email address to send the reset link to.
        token: Token used to validate the user's request.
    """

    # The link sent to the user to reset their password
    reset_url = f"http://{app.config['DOMAIN']}/reset?token={token}"

    # The base URL to the site to indicate where the email is coming from
    site_url = f"http://{app.config['DOMAIN']}/"

    msg = Message("CRC Password Reset", sender="CRC Site", recipients=[email])

    msg.body = render_template(
        "email/password_change.txt",
        email=email,
        site_url=site_url,
        reset_url=reset_url,
    )
    msg.html = render_template(
        "email/password_change.html",
        email=email,
        site_url=site_url,
        reset_url=reset_url,
    )

    mail.send(msg)
