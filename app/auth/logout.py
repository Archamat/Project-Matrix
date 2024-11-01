from flask_login import logout_user
from flask import redirect, url_for, request, flash

def handle_logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))  # Redirect to homepage or login page