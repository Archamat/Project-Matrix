from flask import Blueprint

bp = Blueprint("search", __name__, url_prefix="/search")

from . import routes  # noqa: F401, E402 - Register routes with blueprint
