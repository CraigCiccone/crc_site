"""The main view for the application."""

from flask import flash, redirect, render_template, url_for

from app.blueprints import base
from app.forms import ContactForm
from app.tasks import send_contact_email


@base.route("/", methods=["GET", "POST"])
@base.route("/index", methods=["GET", "POST"])
def index():
    """The main landing page for the application."""
    form = ContactForm()

    if form.validate_on_submit():
        send_contact_email.delay(
            form.first.data,
            form.last.data,
            form.message.data,
            form.email.data,
            form.category.data,
        )
        flash("Message submitted successfully", category="secondary")
        return redirect(url_for("base.index"))

    return render_template("base/index.html", form=form)
