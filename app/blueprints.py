"""All Flask blueprints are defined here."""

from flask import Blueprint

#: List of all blueprints for the application
blueprints = []

#: Each blueprint used in this application
base = Blueprint(name="base", import_name="app.views.base")

# Append all blueprints to the list
blueprints.append(base)
