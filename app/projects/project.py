from app.extensions import db
from flask_login import current_user
from .models import Application
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