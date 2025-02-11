from flask import Blueprint, render_template
from app.projects.models import Project
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def home():
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template('home.html', current_page='home', projects=projects,current_user=current_user)


