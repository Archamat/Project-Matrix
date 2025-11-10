from flask import render_template, redirect, url_for, flash
from .forms import ProjectCreationForm
from .models import Project
from app.extensions import db
from flask_login import current_user
from flask import request, jsonify
from .forms import ApplicationForm
from .models import Application, Task, ChatMessage, ProjectLink, ProjectNote


def handle_project_create():
    form = ProjectCreationForm()
    if form.validate_on_submit():
        # Get form data
        name = form.name.data
        description = form.description.data
        sector = form.sector.data
        people_count = form.people_count.data
        skills = form.skills.data
        creator = current_user

        # Append custom skill if "Other" is selected
        if 'Other' in skills and form.other_skill.data:
            skills.append(form.other_skill.data)

        skills_str = ', '.join(skills)  # Convert list to comma-separated string

        # Create and save project
        project = Project(name=name, description=description, sector=sector, people_count=people_count, skills=skills_str, creator=creator)
        db.session.add(project)
        db.session.commit()

        flash('Project created successfully!', 'success')
        return redirect(url_for('main.home'))  # Update to your desired redirect page

    return render_template('create_project.html', form=form)

def handle_apply_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ApplicationForm()
    
    if form.validate_on_submit():
        skills = form.skills.data
        if 'Other' in skills and form.other_skill.data:
            skills.append(form.other_skill.data)
        
        skills_str = ', '.join(skills)
        
        application = Application(
            project_id=project_id,
            applicant_id=current_user.id,
            information=form.information.data,
            skills=skills_str,
            contact_info=form.contact_info.data
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('apply_project.html', form=form, project=project)


def handle_project_applicants(project_id):
    project = Project.query.get_or_404(project_id)
    # Check if current user is the project creator
    if project.creator_id != current_user.id:
        flash('You are not authorized to view this page', 'error')
        return redirect(url_for('project.projects'))
    return render_template('applicants_list.html', project=project)


def handle_project_gui(project_id):
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
        
        elif action == "delete_task":
            try:
                task_id = int(request.form.get("task_id", "").strip())
            except (ValueError, AttributeError):
                flash("Invalid task ID.", "danger")
                return redirect(url_for("project.project_gui", project_id=project.id))

            task = Task.query.get(task_id)
            if not task or task.project_id != project.id:
                flash("Task not found.", "warning")
                return redirect(url_for("project.project_gui", project_id=project.id))

            db.session.delete(task)
            db.session.commit()
            flash("Task deleted successfully.", "success")
            return redirect(url_for("project.project_gui", project_id=project.id))
               
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