from flask import Blueprint, render_template
from flask_login import login_required
from .project import handle_project_create, handle_apply_project, handle_project_applicants
from .models import Project
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

@project.route('/apply/<int:project_id>', methods=['GET', 'POST'])
@login_required
def apply_project(project_id):
    return handle_apply_project(project_id)

@project.route('/project/<int:project_id>/applicants')
@login_required
def project_applicants(project_id):
    return handle_project_applicants(project_id)