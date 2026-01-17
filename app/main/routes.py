from flask import render_template, jsonify
from app.projects.models import Project
from flask_login import current_user
from . import main


@main.route("/")
def home():
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template(
        "home.html",
        current_page="home",
        projects=projects,
        current_user=current_user,
    )


@main.get("/health")
def health():
    # Keep it lightweight and fast for ALB health checks.
    return jsonify(status="ok"), 200
