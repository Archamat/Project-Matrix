from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .project import (
    handle_project_create, 
    handle_apply_project, 
    handle_project_applicants,
    )
from .models import Project, Task, ChatMessage, ProjectLink, ProjectNote
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


@project.route('/apply/<int:project_id>', methods=['GET', 'POST'])
@login_required
def apply_project(project_id):
    return handle_apply_project(project_id)


@project.route('/project/<int:project_id>/applicants')
@login_required
def project_applicants(project_id):
    return handle_project_applicants(project_id)


@project.route('/project/<int:project_id>/gui', methods=['GET', 'POST'])
@login_required
def project_gui(project_id):
    """Full interactive project GUI (tasks, chat, progress bar, links)"""
    project = Project.query.get_or_404(project_id)

    note = ProjectNote.query.filter_by(
        project_id=project.id,
        author_id=current_user.id,
        title=None
    ).first()
    note_content = note.content if note else ""

    # Handle form actions (optional combined logic)
    action = request.form.get('action')
    if request.method == "POST":
        
        if action == "add_task":
            title = (request.form.get("title") or "").strip()
            if title:
                task = Task(project_id=project.id, title=title)
                db.session.add(task)
                db.session.commit()
            return redirect(url_for('project.project_gui', project_id=project.id))

        elif action == "delete_task":
            task_id = int(request.form["task_id"])
            task = Task.query.get_or_404(task_id)
            if task.project_id == project.id:
                db.session.delete(task)
                db.session.commit()
            return redirect(url_for('project.project_gui', project_id=project.id))
            
        elif action == "toggle_task":
            task_id = int(request.form["task_id"])
            task = Task.query.get_or_404(task_id)
            if task.project_id == project.id:
                task.is_done = not task.is_done
                db.session.commit()
            return redirect(url_for('project.project_gui', project_id=project.id))

        elif action == "add_message":
            body = (request.form.get("body") or "").strip()
            if body:
                msg = ChatMessage(project_id=project.id, author_id=current_user.id, body=body)
                db.session.add(msg)
                db.session.commit()
            return redirect(url_for('project.project_gui', project_id=project.id))

        elif action == "add_link":
            label = (request.form.get("label") or "").strip()
            url = (request.form.get("url") or "").strip()
            if label and url:
                link = ProjectLink(project_id=project.id, label=label, url=url)
                db.session.add(link)
                db.session.commit()
            return redirect(url_for('project.project_gui', project_id=project.id))
        
        elif action == "delete_link":
            link_id = int(request.form["link_id"])
            link = ProjectLink.query.get_or_404(link_id)
            # Only allow deletion if link belongs to this project
            if link.project_id == project.id:
                db.session.delete(link)
                db.session.commit()
            return redirect(url_for('project.project_gui', project_id=project.id))
               
        elif action == "save_note":
            content = (request.form.get("content") or "").strip()
            if note is None:
                note = ProjectNote(
                    project_id=project.id,
                    author_id=current_user.id,
                    title=None,
                    content=content
                )
                db.session.add(note)
            else:
                note.content = content
            db.session.commit()
        
            # Compute progress
    total = len(project.tasks)
    done = sum(1 for t in project.tasks if t.is_done)
    progress = int((done / total) * 100) if total > 0 else 0

    return render_template(
        'project_gui.html',
        project=project,
        progress=progress,
        note_content=note_content
    )