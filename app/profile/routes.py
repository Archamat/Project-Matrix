from flask import Blueprint, render_template
from flask_login import login_required
from .profile import handle_profile

profile = Blueprint('profile', __name__)

@profile.route('/profile')
@login_required
def show_profile():
    return handle_profile()


