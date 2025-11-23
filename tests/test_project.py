"""
Unit tests for the projects module.

Tests cover:
- Project creation logic
- Project retrieval
- Application to projects
- Project GUI actions (tasks, chat, links, notes)
- Authorization checks
"""

import pytest
from datetime import datetime
from app import create_app, db
from app.auth.models import User
from app.projects.models import Project, Application, Task, ChatMessage, ProjectLink, ProjectNote
from app.projects.project import (
    handle_project_create,
    handle_apply_project,
    get_project_by_id,
    get_all_projects,
    get_project_applicants
)
from app.projects.project_database_manager import ProjectDatabaseManager


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for the Flask application"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def test_project(app, test_user):
    """Create a test project"""
    with app.app_context():
        user = User.query.get(test_user)
        project = Project(
            name='Test Project',
            description='Test Description',
            sector='Technology',
            people_count=5,
            skills='Python, Flask',
            creator=user
        )
        db.session.add(project)
        db.session.commit()
        return project.id


# ==================== PROJECT CREATION TESTS ====================

class TestProjectCreation:
    """Tests for project creation functionality"""
    
    def test_create_project_success(self, app, test_user):
        """Test successful project creation"""
        with app.app_context():
            handle_project_create(
                name='New Project',
                description='A great project',
                sector='Technology',
                people_count=3,
                skills=['Python', 'JavaScript'],
                creator_id=test_user
            )
            
            project = Project.query.filter_by(name='New Project').first()
            assert project is not None
            assert project.description == 'A great project'
            assert project.sector == 'Technology'
            assert project.people_count == 3
            assert 'Python' in project.skills
            assert project.creator_id == test_user
    
    def test_create_project_with_other_skill(self, app, test_user):
        """Test project creation with custom 'Other' skill"""
        with app.app_context():
            handle_project_create(
                name='Custom Skills Project',
                description='Test',
                sector='Art',
                people_count=2,
                skills=['Other', 'Python'],
                other_skill='Custom Skill',
                creator_id=test_user
            )
            
            project = Project.query.filter_by(name='Custom Skills Project').first()
            assert project is not None
            assert 'Custom Skill' in project.skills
    
    def test_create_project_short_name(self, app, test_user):
        """Test project creation fails with short name"""
        with app.app_context():
            with pytest.raises(ValueError, match="at least 3 characters"):
                handle_project_create(
                    name='AB',
                    description='Test',
                    sector='Tech',
                    people_count=1,
                    creator_id=test_user
                )
    
    def test_create_project_empty_name(self, app, test_user):
        """Test project creation fails with empty name"""
        with app.app_context():
            with pytest.raises(ValueError, match="at least 3 characters"):
                handle_project_create(
                    name='   ',
                    description='Test',
                    sector='Tech',
                    people_count=1,
                    creator_id=test_user
                )
    
    def test_create_project_strips_whitespace(self, app, test_user):
        """Test project name is trimmed"""
        with app.app_context():
            handle_project_create(
                name='   Trimmed Project   ',
                description='Test',
                sector='Tech',
                people_count=1,
                creator_id=test_user
            )
            
            project = Project.query.filter_by(name='Trimmed Project').first()
            assert project is not None
            assert project.name == 'Trimmed Project'


# ==================== PROJECT RETRIEVAL TESTS ====================

class TestProjectRetrieval:
    """Tests for project retrieval operations"""
    
    def test_get_project_by_id(self, app, test_project):
        """Test retrieving a project by ID"""
        with app.app_context():
            project = get_project_by_id(test_project)
            assert project is not None
            assert project.id == test_project
            assert project.name == 'Test Project'
    
    def test_get_project_by_invalid_id(self, app):
        """Test retrieving a non-existent project"""
        with app.app_context():
            project = get_project_by_id(99999)
            assert project is None
    
    def test_get_all_projects(self, app, test_user):
        """Test retrieving all projects"""
        with app.app_context():
            # Create multiple projects
            for i in range(3):
                handle_project_create(
                    name=f'Project {i}',
                    description=f'Description {i}',
                    sector='Tech',
                    people_count=2,
                    creator_id=test_user
                )
            
            projects = get_all_projects()
            assert len(projects) >= 3
    
    def test_project_to_dict(self, app, test_project):
        """Test project serialization"""
        with app.app_context():
            project = Project.query.get(test_project)
            data = project.to_dict()
            
            assert data['id'] == test_project
            assert data['name'] == 'Test Project'
            assert data['description'] == 'Test Description'
            assert data['sector'] == 'Technology'
            assert data['people_count'] == 5
            assert isinstance(data['skills'], list)
            assert 'Python' in data['skills']


# ==================== APPLICATION TESTS ====================

class TestProjectApplications:
    """Tests for project application functionality"""
    
    def test_apply_to_project(self, app, test_project, test_user):
        """Test successful application to project"""
        with app.app_context():
            # Create applicant
            applicant = User(username='applicant', email='applicant@test.com')
            applicant.set_password('password')
            db.session.add(applicant)
            db.session.commit()
            
            form_data = {
                'skills': ['Python', 'JavaScript'],
                'other_skill': '',
                'information': 'I am interested in this project',
                'contact_info': 'applicant@test.com'
            }
            
            # Mock current_user by setting up application context
            from flask_login import login_user
            with app.test_request_context():
                login_user(applicant)
                handle_apply_project(test_project, form_data, applicant.id)
            
            # Verify application was created
            application = Application.query.filter_by(
                project_id=test_project,
                applicant_id=applicant.id
            ).first()
            
            assert application is not None
            assert application.information == 'I am interested in this project'
            assert 'Python' in application.skills
    
    def test_get_project_applicants(self, app, test_project, test_user):
        """Test retrieving project applicants"""
        with app.app_context():
            # Create and apply with an applicant
            applicant = User(username='applicant2', email='applicant2@test.com')
            applicant.set_password('password')
            db.session.add(applicant)
            db.session.commit()
            
            application = Application(
                project_id=test_project,
                applicant_id=applicant.id,
                information='Test info',
                skills='Python',
                contact_info='test@test.com'
            )
            db.session.add(application)
            db.session.commit()
            
            # Get applicants as creator
            applicants = get_project_applicants(test_project, test_user)
            assert len(applicants) == 1
            assert applicants[0].applicant_id == applicant.id
    
    def test_get_applicants_unauthorized(self, app, test_project, test_user):
        """Test unauthorized access to applicants"""
        with app.app_context():
            # Create another user (not creator)
            other_user = User(username='other', email='other@test.com')
            other_user.set_password('password')
            db.session.add(other_user)
            db.session.commit()
            
            with pytest.raises(PermissionError, match="don't have permission"):
                get_project_applicants(test_project, other_user.id)


# ==================== DATABASE MANAGER TESTS ====================

class TestProjectDatabaseManager:
    """Tests for ProjectDatabaseManager operations"""
    
    def test_create_project_via_manager(self, app, test_user):
        """Test project creation through database manager"""
        with app.app_context():
            manager = ProjectDatabaseManager()
            project = manager.create_project(
                name='Manager Project',
                description='Created by manager',
                sector='Business',
                people_count=4,
                skills='Management, Leadership',
                creator_id=test_user
            )
            
            assert project.id is not None
            assert project.name == 'Manager Project'
    
    def test_create_project_invalid_creator(self, app):
        """Test project creation with invalid creator ID"""
        with app.app_context():
            manager = ProjectDatabaseManager()
            with pytest.raises(ValueError, match="Invalid creator ID"):
                manager.create_project(
                    name='Invalid Project',
                    description='Test',
                    sector='Tech',
                    people_count=1,
                    skills='Python',
                    creator_id=99999
                )
    
    def test_add_element_to_project(self, app, test_project):
        """Test adding elements (task, link) to project"""
        with app.app_context():
            manager = ProjectDatabaseManager()
            
            # Add a task
            task = Task(project_id=test_project, title='Test Task')
            result = manager.add_element_to_project(test_project, task)
            
            assert result.id is not None
            assert result.title == 'Test Task'
            
            # Verify task is linked to project
            project = Project.query.get(test_project)
            assert len(project.tasks) == 1
    
    def test_delete_element_from_project(self, app, test_project):
        """Test deleting elements from project"""
        with app.app_context():
            # Create a task
            task = Task(project_id=test_project, title='To Delete')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
            
            # Delete it
            manager = ProjectDatabaseManager()
            manager.delete_element_from_project(task)
            
            # Verify deletion
            deleted_task = Task.query.get(task_id)
            assert deleted_task is None


# ==================== PROJECT MODELS TESTS ====================

class TestProjectModels:
    """Tests for Project-related models"""
    
    def test_task_creation(self, app, test_project):
        """Test creating a task"""
        with app.app_context():
            task = Task(project_id=test_project, title='New Task', is_done=False)
            db.session.add(task)
            db.session.commit()
            
            assert task.id is not None
            assert task.title == 'New Task'
            assert task.is_done is False
    
    def test_task_toggle(self, app, test_project):
        """Test toggling task completion"""
        with app.app_context():
            task = Task(project_id=test_project, title='Toggle Task')
            db.session.add(task)
            db.session.commit()
            
            # Toggle
            task.is_done = not task.is_done
            db.session.commit()
            
            assert task.is_done is True
    
    def test_chat_message_creation(self, app, test_project, test_user):
        """Test creating a chat message"""
        with app.app_context():
            message = ChatMessage(
                project_id=test_project,
                author_id=test_user,
                body='Hello, team!'
            )
            db.session.add(message)
            db.session.commit()
            
            assert message.id is not None
            assert message.body == 'Hello, team!'
            assert message.created_at is not None
    
    def test_project_link_creation(self, app, test_project):
        """Test creating a project link"""
        with app.app_context():
            link = ProjectLink(
                project_id=test_project,
                label='Documentation',
                url='https://example.com/docs'
            )
            db.session.add(link)
            db.session.commit()
            
            assert link.id is not None
            assert link.label == 'Documentation'
            assert link.url == 'https://example.com/docs'
    
    def test_project_note_creation(self, app, test_project, test_user):
        """Test creating a project note"""
        with app.app_context():
            note = ProjectNote(
                project_id=test_project,
                author_id=test_user,
                content='Important notes here',
                title='Meeting Notes'
            )
            db.session.add(note)
            db.session.commit()
            
            assert note.id is not None
            assert note.content == 'Important notes here'
            assert note.title == 'Meeting Notes'
    
    def test_project_relationships(self, app, test_project, test_user):
        """Test project relationships (tasks, messages, links, notes)"""
        with app.app_context():
            project = Project.query.get(test_project)
            
            # Add related entities
            task = Task(project_id=test_project, title='Task 1')
            message = ChatMessage(project_id=test_project, author_id=test_user, body='Message 1')
            link = ProjectLink(project_id=test_project, label='Link 1', url='http://test.com')
            note = ProjectNote(project_id=test_project, author_id=test_user, content='Note 1')
            
            db.session.add_all([task, message, link, note])
            db.session.commit()
            
            # Refresh and verify relationships
            db.session.refresh(project)
            assert len(project.tasks) == 1
            assert len(project.messages) == 1
            assert len(project.links) == 1
            assert len(project.notes) == 1
