from flask import Blueprint, render_template
from flask_login import login_required
from .profile import handle_profile,update_profile

profile = Blueprint('profile', __name__)

@profile.route('/profile')
@login_required
def show_profile():
    return handle_profile()


@profile.route('/profile/update', methods=['POST'])
def update_profile_info():
    return update_profile()