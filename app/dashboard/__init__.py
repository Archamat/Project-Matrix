from flask import Blueprint

# Create blueprint
dashboard = Blueprint("dashboard", __name__)

# Import routes to register them
from . import routes  # noqa: F401, E402
