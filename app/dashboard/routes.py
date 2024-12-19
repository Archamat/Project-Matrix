from flask import Blueprint, render_template
from flask_login import login_required
from .dashboard import handle_dashboard

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def show_dashboard():
    return handle_dashboard()


