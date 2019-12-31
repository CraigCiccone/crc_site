"""All Flask blueprints are defined here."""

from typing import List

from flask import Blueprint

from app.extensions import csrf

#: List of all blueprints for the application
blueprints: List[Blueprint] = []

# Each blueprint used in this application
admin: Blueprint = Blueprint(name="admin", import_name="app.views.admin")
api: Blueprint = Blueprint(name="api", import_name="app.views.api")
base: Blueprint = Blueprint(name="base", import_name="app.views.base")
user: Blueprint = Blueprint(name="user", import_name="app.views.user")

# Do not use CSRF protection on APIs. They are secured via JWT
csrf.exempt(api)

# Append all blueprints to the list
blueprints.append(admin)
blueprints.append(api)
blueprints.append(base)
blueprints.append(user)
