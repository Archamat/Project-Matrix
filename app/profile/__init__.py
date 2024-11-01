from flask import Blueprint
# Define the blueprint: the 'auth' blueprint will handle login, register, etc.
prfile = Blueprint('profile', __name__)
from .routes import profile
