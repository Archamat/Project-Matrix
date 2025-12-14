from flask import Blueprint

# Define blueprints here
profile = Blueprint("profile", __name__)
profile_api = Blueprint("profile_api", __name__, url_prefix="/api/profile")

# Import routes AFTER blueprint creation
from . import routes  # noqa: F401, E402
from . import api  # noqa: F401, E402

__all__ = ["profile", "profile_api"]
