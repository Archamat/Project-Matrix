from flask import Blueprint
from .models import User
from app.extensions import login_manager

# Define the blueprint
auth = Blueprint("auth", __name__)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Import routes AFTER blueprint creation
from . import routes  # noqa: F401, E402
