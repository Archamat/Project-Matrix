from .models import Project
from app.auth.models import User
from app.extensions import db


class ProjectDatabaseManager:
    @staticmethod
    def create_project(name, description, sector, people_count, skills,
                       creator_id):
        creator = User.query.get(creator_id)
        if not creator:
            raise ValueError("Invalid creator ID")

        project = Project(
            name=name,
            description=description,
            sector=sector,
            people_count=people_count,
            skills=skills,
            creator=creator
        )
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def get_project_by_id(project_id):
        return Project.query.get(project_id)

    @staticmethod
    def get_all_projects():
        return Project.query.all()

    @staticmethod
    def apply_to_project(project_id, user_id, application):
        project = Project.query.get(project_id)
        user = User.query.get(user_id)

        if not project:
            raise ValueError("Project not found")
        if not user:
            raise ValueError("User not found")

        db.session.add(application)
        db.session.commit()
        return application

    @staticmethod
    def add_element_to_project(project_id, element):
        project = Project.query.get(project_id)
        if not project:
            raise ValueError("Project not found")

        db.session.add(element)
        db.session.commit()
        return element
    
    @staticmethod
    def delete_element_from_project(element):
        db.session.delete(element)
        db.session.commit()
