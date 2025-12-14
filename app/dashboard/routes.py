from . import dashboard  # Import blueprint from __init__.py
from .dashboard import handle_dashboard


@dashboard.route("/dashboard")
def show_dashboard():
    return handle_dashboard()
