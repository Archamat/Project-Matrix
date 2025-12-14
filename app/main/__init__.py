from flask import Blueprint

# Define the blueprint
main = Blueprint("main", __name__)

# Import routes AFTER blueprint creation
from . import routes  # noqa: F401, E402
