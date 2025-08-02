from flask import render_template, redirect, url_for, flash
from .forms import ProjectCreationForm
from .models import Project
from app.extensions import db
from flask_login import current_user
from flask import request, jsonify
from .forms import ApplicationForm
from .models import Application

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