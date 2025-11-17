from app.extensions import db
from flask_login import current_user
from flask import request, jsonify
from .forms import ApplicationForm
from .models import Application, Task, ChatMessage, ProjectLink, ProjectNote

from .project_database_manager import ProjectDatabaseManager


def handle_project_create(name=None, description=None, sector=None, 
                          people_count=None, skills=None, other_skill=None,
                          creator_id=None):
    try:
        if not name or len(name.strip()) < 3:
            raise ValueError("Project name must be at least 3 characters long")

        # Append custom skill if "Other" is selected
        if isinstance(skills, list):
            if 'Other' in skills and other_skill:
                skills.append(other_skill)
            skills_str = ', '.join(skills)
        else:
            skills_str = skills or ''

        # Create and save project
        database_manager = ProjectDatabaseManager()
        database_manager.create_project(
            name=name.strip(),
            description=description,
            sector=sector,
            people_count=people_count,
            skills=skills_str,
            creator_id=creator_id
        )

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Failed to create project: {str(e)}")


def handle_apply_project(project_id, form, creator_id):

    try:
        skills = form["skills"]
        if 'Other' in skills and form["other_skill"]:
            skills.append(form["other_skill"])
        skills_str = ', '.join(skills)
        application = Application(
            project_id=project_id,
            applicant_id=current_user.id,
            information=form["information"],
            skills=skills_str,
            contact_info=form["contact_info"]
        )
        database_manager = ProjectDatabaseManager()
        database_manager.apply_to_project(project_id, creator_id,
                                          application)
    except Exception:
        db.session.rollback()
        raise ValueError("Failed to apply to project")


def handle_project_gui(project_id):
    """Full interactive project GUI (tasks, chat, progress bar, links)"""
    project = ProjectDatabaseManager.get_project_by_id(project_id)

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
                ProjectDatabaseManager.add_element_to_project(project.id, task)

        elif action == "delete_task":
            task_id = int(request.form["task_id"])
            task = Task.query.get_or_404(task_id)
            if task.project_id == project.id:
                ProjectDatabaseManager.delete_element_from_project(task)
            
        elif action == "toggle_task":
            task_id = int(request.form["task_id"])
            task = Task.query.get_or_404(task_id)
            if task.project_id == project.id:
                task.is_done = not task.is_done
                db.session.commit()

        elif action == "add_message":
            body = (request.form.get("body") or "").strip()
            if body:
                msg = ChatMessage(project_id=project.id, author_id=current_user.id, body=body)
                db.session.add(msg)
                db.session.commit()

        elif action == "add_link":
            label = (request.form.get("label") or "").strip()
            url = (request.form.get("url") or "").strip()
            if label and url:
                link = ProjectLink(project_id=project.id, label=label, url=url)
                ProjectDatabaseManager.add_element_to_project(project.id, link)
        
        elif action == "delete_task":
            try:
                task_id = int(request.form.get("task_id", "").strip())
            except (ValueError, AttributeError):
                raise ValueError("Invalid task ID")
            task = Task.query.get(task_id)
            if not task or task.project_id != project.id:
                raise ValueError("Task not found.")

            ProjectDatabaseManager.delete_element_from_project(task)
               
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

    return {
        "project": project,
        "tasks": project.tasks,
        "messages": project.messages,
        "links": project.links,
        "note_content": note_content,
        "progress": progress
    }


def get_project_applicants(project_id, creator_id):
    # Check if current user is the project creator
    project = get_project_by_id(project_id)

    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Check authorization
    if project.creator_id != creator_id:
        raise PermissionError("You don't have "
                              "permission to view these applicants")

    # Return the applicants (empty list if none)
    return project.applications


def get_project_by_id(project_id):
    database_manager = ProjectDatabaseManager()
    return database_manager.get_project_by_id(project_id)


def get_all_projects():
    database_manager = ProjectDatabaseManager()
    return database_manager.get_all_projects()
