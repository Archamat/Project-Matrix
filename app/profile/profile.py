from flask import render_template
from flask_login import current_user

def handle_profile():
    return render_template('profile.html', user=current_user, current_page='profile')
