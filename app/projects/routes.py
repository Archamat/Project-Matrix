from flask import render_template
from flask_login import login_required
from . import project
from .project import get_project_by_id, handle_project_gui, get_all_projects
from .forms import ProjectCreationForm, ApplicationForm


@project.route("/projects")
def projects():
    projects = get_all_projects()
    return render_template("projects.html", projects=projects)


@project.route("/project/<int:project_id>")
def project_detail(project_id):
    project = get_project_by_id(project_id)
    return render_template("project_detail.html", project=project)


@project.route("/create_project", methods=["GET", "POST"])
@login_required
def create_project():
    form = ProjectCreationForm()
    return render_template("create_project.html", form=form)


@project.route("/apply/<int:project_id>", methods=["GET", "POST"])
@login_required
def apply_project(project_id):
    form = ApplicationForm()
    project = get_project_by_id(project_id)
    return render_template("apply_project.html", project=project, form=form)


@project.route("/project/<int:project_id>/applicants")
@login_required
def project_applicants(project_id):
    project = get_project_by_id(project_id)
    return render_template("applicants_list.html", project=project)


@project.route("/project/<int:project_id>/gui", methods=["GET", "POST"])
@login_required
def project_gui(project_id):
    project_gui = handle_project_gui(project_id)
    return render_template(
        "project_gui.html",
        project=project_gui["project"],
        progress=project_gui["progress"],
        note_content=project_gui["note_content"],
    )
