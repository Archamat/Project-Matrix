from flask import Blueprint

# Define blueprints here
project = Blueprint("project", __name__)
project_api = Blueprint("project_api", __name__)

# Import routes AFTER blueprint creation
from . import routes  # noqa: F401, E402
from . import api  # noqa: F401, E402
