from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from .project import (handle_project_create, handle_apply_project, 
                      get_project_applicants, 
                      get_project_by_id, get_all_projects)
from .forms import ProjectCreationForm, ApplicationForm

project = Blueprint('project', __name__)


@project.route('/projects')
def projects():
    projects = get_all_projects()
    return render_template('projects.html', projects=projects)


@project.route('/project/<int:project_id>')
def project_detail(project_id):
    project = get_project_by_id(project_id)
    return render_template('project_detail.html', project=project)


@project.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectCreationForm()
    return render_template('create_project.html', form=form)


@project.route('/apply/<int:project_id>', methods=['GET', 'POST'])
@login_required
def apply_project(project_id):
    form = ApplicationForm()
    project = get_project_by_id(project_id)
    return render_template('apply_project.html', project=project,
                           form=form)


@project.route('/project/<int:project_id>/applicants')
@login_required
def project_applicants(project_id):
    project = get_project_by_id(project_id)
    return render_template('applicants_list.html', project=project)