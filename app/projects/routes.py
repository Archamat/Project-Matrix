from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from .project import handle_project_create
from .models import Project
from app.extensions import db

project = Blueprint('project', __name__)

@project.route('/projects')
def projects():
    projects = Project.query.all()  # Fetches all projects
    return render_template('projects.html', projects=projects)

@project.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@project.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    return handle_project_create()