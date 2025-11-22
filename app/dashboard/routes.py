from flask import Blueprint
from .dashboard import handle_dashboard

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def show_dashboard():
    return handle_dashboard()
