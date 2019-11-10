from flask import render_template

from app.blueprints import base


@base.route("/", methods=["GET"])
@base.route("/index", methods=["GET"])
def index():
    """The base page of the application. Simply returns the HTML template."""

    return render_template("base/index.html")
