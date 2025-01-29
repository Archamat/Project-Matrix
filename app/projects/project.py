from flask import render_template, redirect, url_for, flash
from .forms import ProjectCreationForm
from .models import Project
from app.extensions import db
from flask_login import current_user

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