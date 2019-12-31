"""Application views that are limited to admin users."""

from flask import render_template
from flask_login import login_required

from app.blueprints import admin
from app.models.db import User
from app.utils.auth import required_roles_ui


@admin.route("/admin", methods=["GET", "POST"])
@required_roles_ui(*["admin"])
@login_required
def adm():
    """The admin portal showing all registered users in a table."""
    users = User.query.all()
    return render_template("admin/admin.html", users=users)
