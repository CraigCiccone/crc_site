"""All Flask forms are defined here."""

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.widgets import TextArea


class ContactForm(FlaskForm):
    """Form data used to send a message delivered via email."""

    category = SelectField(
        "Category",
        validators=[Optional()],
        choices=[
            ("About", "About This Site"),
            ("Work", "Work Related"),
            ("Game Development", "Game Development"),
            ("Other", "Other"),
        ],
    )
    email = StringField(
        "Email",
        validators=[Optional(), Length(max=256), Email()],
        render_kw={"maxlength": "256", "placeholder": "Email"},
    )
    first = StringField(
        "*First Name",
        validators=[DataRequired(message="Required"), Length(max=32)],
        render_kw={"maxlength": "32", "placeholder": "First Name"},
    )
    last = StringField(
        "*Last Name",
        validators=[DataRequired(message="Required"), Length(max=32)],
        render_kw={"maxlength": "32", "placeholder": "Last Name"},
    )
    message = StringField(
        "*Message",
        validators=[DataRequired(message="Required"), Length(max=2048)],
        widget=TextArea(),
        render_kw={"maxlength": "2048", "placeholder": "Message Content"},
    )
    submit_recap = SubmitField("Submit Message")
    recaptcha = RecaptchaField("reCAPTCHA")


class LoginForm(FlaskForm):
    """Form data used to try to log into the application."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Required"),
            Length(max=256),
            Email(),
        ],
        render_kw={"maxlength": "256", "placeholder": "*Email"},
    )
    pw = PasswordField(
        "Password",
        validators=[DataRequired(message="Required"), Length(max=32)],
        render_kw={"maxlength": "32", "placeholder": "*Password"},
    )
    remember = BooleanField("Remember me", default=False)
    submit_recap = SubmitField("Login")
    recaptcha = RecaptchaField("reCAPTCHA")


class PasswordForm(FlaskForm):
    """Captures a user password including a password confirmation."""

    pw = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Required"),
            Length(max=32),
            EqualTo("confirm", message="Passwords must match"),
        ],
        render_kw={"maxlength": "32", "placeholder": "*Password"},
    )
    confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(message="Required")],
        render_kw={"maxlength": "32", "placeholder": "*Confirm Password"},
    )
    submit = SubmitField("Submit")


class RecoverForm(FlaskForm):
    """Form data used to recover a forgotten password."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Required"),
            Length(max=32),
            Email(),
            EqualTo("confirm", message="Emails must match"),
        ],
        render_kw={"maxlength": "256", "placeholder": "*Email"},
    )
    confirm = StringField(
        "Confirm Email",
        validators=[DataRequired(message="Required")],
        render_kw={"maxlength": "256", "placeholder": "*Confirm Email"},
    )
    submit_recap = SubmitField("Recover")
    recaptcha = RecaptchaField("reCAPTCHA")


class RegisterForm(FlaskForm):
    """Form data used to register a new account with the website."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Required"),
            Length(max=256),
            Email(),
        ],
        render_kw={"maxlength": "256", "placeholder": "*Email"},
    )
    pw = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Required"),
            Length(min=8, max=32),
            EqualTo("confirm", message="Passwords must match"),
        ],
        render_kw={"maxlength": "32", "placeholder": "*Password"},
    )
    confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(message="Required")],
        render_kw={"maxlength": "32", "placeholder": "*Confirm Password"},
    )
    submit_recap = SubmitField("Register")
    recaptcha = RecaptchaField("reCAPTCHA")
