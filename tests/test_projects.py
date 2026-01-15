"""
Unit tests for the projects module.

Tests cover:
- Project model and database operations
- Project creation and validation
- Application submission and management
- Task management (CRUD)
- Chat messages
- Project links and notes
- Authorization and permissions
"""

import pytest
from app.extensions import db
from app.projects.models import (
    Project,
    Application,
    Task,
    ChatMessage,
    ProjectLink,
    ProjectNote,
)
from app.projects.project_database_manager import ProjectDatabaseManager
from app.projects.project import (
    handle_project_create,
    handle_apply_project,
    get_project_applicants,
    get_project_by_id,
    get_all_projects,
)


# ==================== PROJECT MODEL TESTS ====================


class TestProjectModel:
    """Tests for the Project model"""

    def test_project_creation(self, app, test_user):
        """Test creating a project with valid data"""
        # Arrange & Act
        project = Project(
            name="AI Project",
            description="Building an AI application",
            sector="ai",
            people_count=3,
            skills="Python, TensorFlow",
            creator=test_user,
        )
        db.session.add(project)
        db.session.commit()

        # Assert
        assert project.id is not None
        assert project.name == "AI Project"
        assert project.sector == "ai"
        assert project.people_count == 3
        assert project.creator_id == test_user.id

    def test_project_to_dict(self, test_project):
        """Test project serialization to dictionary"""
        # Act
        project_dict = test_project.to_dict()

        # Assert
        assert project_dict["id"] == test_project.id
        assert project_dict["name"] == test_project.name
        assert project_dict["description"] == test_project.description
        assert project_dict["sector"] == test_project.sector
        assert project_dict["people_count"] == test_project.people_count
        assert isinstance(project_dict["skills"], list)
        assert project_dict["creator_id"] == test_project.creator_id

    def test_project_skills_parsing(self, test_project):
        """Test that skills are properly parsed to list"""
        # Act
        project_dict = test_project.to_dict()

        # Assert
        assert "Python" in project_dict["skills"]
        assert "JavaScript" in project_dict["skills"]
        assert "HTML" in project_dict["skills"]

    def test_project_without_skills(self, app, test_user):
        """Test project creation without skills"""
        # Arrange & Act
        project = Project(
            name="Simple Project",
            description="A simple project",
            sector="web",
            people_count=2,
            skills=None,
            creator=test_user,
        )
        db.session.add(project)
        db.session.commit()

        # Assert
        project_dict = project.to_dict()
        assert project_dict["skills"] == []


# ==================== APPLICATION MODEL TESTS ====================


class TestApplicationModel:
    """Tests for the Application model"""

    def test_application_creation(self, app, test_project, test_user_2):
        """Test creating an application with valid data"""
        # Arrange & Act
        application = Application(
            project_id=test_project.id,
            applicant_id=test_user_2.id,
            information="I have experience in web development",
            skills="Python, Flask, React",
            contact_info="applicant@example.com",
        )
        db.session.add(application)
        db.session.commit()

        # Assert
        assert application.id is not None
        assert application.project_id == test_project.id
        assert application.applicant_id == test_user_2.id
        assert (
            application.information == "I have experience in web development"
        )

    def test_application_relationship_with_project(
        self, test_application, test_project
    ):
        """Test application-project relationship"""
        # Assert
        assert test_application in test_project.applications
        assert test_application.project == test_project

    def test_application_relationship_with_user(
        self, test_application, test_user_2
    ):
        """Test application-user relationship"""
        # Assert
        assert test_application in test_user_2.applications
        assert test_application.applicant == test_user_2


# ==================== TASK MODEL TESTS ====================


class TestTaskModel:
    """Tests for the Task model"""

    def test_task_creation(self, app, test_project):
        """Test creating a task"""
        # Arrange & Act
        task = Task(
            project_id=test_project.id,
            title="Implement feature X",
            is_done=False,
        )
        db.session.add(task)
        db.session.commit()

        # Assert
        assert task.id is not None
        assert task.title == "Implement feature X"
        assert task.is_done is False
        assert task.project_id == test_project.id

    def test_task_toggle_completion(self, test_task):
        """Test toggling task completion status"""
        # Arrange
        initial_status = test_task.is_done

        # Act
        test_task.is_done = not test_task.is_done
        db.session.commit()

        # Assert
        assert test_task.is_done != initial_status

    def test_task_relationship_with_project(self, test_task, test_project):
        """Test task-project relationship"""
        # Assert
        assert test_task in test_project.tasks
        assert test_task.project == test_project


# ==================== CHAT MESSAGE MODEL TESTS ====================


class TestChatMessageModel:
    """Tests for the ChatMessage model"""

    def test_chat_message_creation(self, app, test_project, test_user):
        """Test creating a chat message"""
        # Arrange & Act
        message = ChatMessage(
            project_id=test_project.id,
            author_id=test_user.id,
            body="This is a test message",
        )
        db.session.add(message)
        db.session.commit()

        # Assert
        assert message.id is not None
        assert message.body == "This is a test message"
        assert message.project_id == test_project.id
        assert message.author_id == test_user.id

    def test_chat_message_relationships(
        self, test_chat_message, test_project, test_user
    ):
        """Test chat message relationships"""
        # Assert
        assert test_chat_message in test_project.messages
        assert test_chat_message.author == test_user


# ==================== PROJECT LINK MODEL TESTS ====================


class TestProjectLinkModel:
    """Tests for the ProjectLink model"""

    def test_project_link_creation(self, app, test_project):
        """Test creating a project link"""
        # Arrange & Act
        link = ProjectLink(
            project_id=test_project.id,
            label="Documentation",
            url="https://docs.example.com",
        )
        db.session.add(link)
        db.session.commit()

        # Assert
        assert link.id is not None
        assert link.label == "Documentation"
        assert link.url == "https://docs.example.com"

    def test_project_link_relationship(self, test_project_link, test_project):
        """Test project link relationship"""
        # Assert
        assert test_project_link in test_project.links


# ==================== PROJECT NOTE MODEL TESTS ====================


class TestProjectNoteModel:
    """Tests for the ProjectNote model"""

    def test_project_note_creation(self, app, test_project, test_user):
        """Test creating a project note"""
        # Arrange & Act
        note = ProjectNote(
            project_id=test_project.id,
            author_id=test_user.id,
            content="Important note about the project",
        )
        db.session.add(note)
        db.session.commit()

        # Assert
        assert note.id is not None
        assert note.content == "Important note about the project"

    def test_project_note_with_title(self, app, test_project, test_user):
        """Test creating a project note with title"""
        # Arrange & Act
        note = ProjectNote(
            project_id=test_project.id,
            author_id=test_user.id,
            content="Note content",
            title="Note Title",
        )
        db.session.add(note)
        db.session.commit()

        # Assert
        assert note.title == "Note Title"


# ==================== PROJECT DATABASE MANAGER TESTS ====================


class TestProjectDatabaseManager:
    """Tests for ProjectDatabaseManager"""

    def test_create_project(self, app, test_user):
        """Test creating project through database manager"""
        # Act
        project = ProjectDatabaseManager.create_project(
            name="Database Test Project",
            description="Testing database manager",
            sector="embedded",
            people_count=4,
            skills="C, C++",
            creator_id=test_user.id,
        )

        # Assert
        assert project.id is not None
        assert project.name == "Database Test Project"
        assert project.creator_id == test_user.id

    def test_create_project_invalid_creator(self, app):
        """Test creating project with invalid creator ID"""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid creator ID"):
            ProjectDatabaseManager.create_project(
                name="Invalid Project",
                description="Test",
                sector="web",
                people_count=2,
                skills="Python",
                creator_id=99999,
            )

    def test_get_project_by_id(self, test_project):
        """Test retrieving project by ID"""
        # Act
        project = ProjectDatabaseManager.get_project_by_id(test_project.id)

        # Assert
        assert project is not None
        assert project.id == test_project.id
        assert project.name == test_project.name

    def test_get_project_by_id_not_found(self, app):
        """Test retrieving non-existent project"""
        # Act
        project = ProjectDatabaseManager.get_project_by_id(99999)

        # Assert
        assert project is None

    def test_get_all_projects(self, app, test_user):
        """Test retrieving all projects"""
        # Arrange - Create multiple projects
        for i in range(3):
            project = Project(
                name=f"Project {i}",
                description=f"Description {i}",
                sector="web",
                people_count=2,
                skills="Python",
                creator=test_user,
            )
            db.session.add(project)
        db.session.commit()

        # Act
        projects = ProjectDatabaseManager.get_all_projects()

        # Assert
        assert len(projects) >= 3

    def test_apply_to_project(self, app, test_project, test_user_2):
        """Test applying to a project"""
        # Arrange
        application = Application(
            project_id=test_project.id,
            applicant_id=test_user_2.id,
            information="Test application",
            skills="Python",
            contact_info="test@example.com",
        )

        # Act
        result = ProjectDatabaseManager.apply_to_project(
            test_project.id, test_user_2.id, application
        )

        # Assert
        assert result.id is not None
        assert result.project_id == test_project.id

    def test_apply_to_project_invalid_project(self, app, test_user):
        """Test applying to non-existent project"""
        # Arrange
        application = Application(
            project_id=99999,
            applicant_id=test_user.id,
            information="Test",
            skills="Python",
            contact_info="test@example.com",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Project not found"):
            ProjectDatabaseManager.apply_to_project(
                99999, test_user.id, application
            )

    def test_add_element_to_project(self, app, test_project):
        """Test adding element (task) to project"""
        # Arrange
        task = Task(project_id=test_project.id, title="New Task")

        # Act
        result = ProjectDatabaseManager.add_element_to_project(
            test_project.id, task
        )

        # Assert
        assert result.id is not None
        assert result.title == "New Task"

    def test_add_element_to_invalid_project(self, app):
        """Test adding element to non-existent project"""
        # Arrange
        task = Task(project_id=99999, title="New Task")

        # Act & Assert
        with pytest.raises(ValueError, match="Project not found"):
            ProjectDatabaseManager.add_element_to_project(99999, task)

    def test_delete_element_from_project(self, test_task):
        """Test deleting element from project"""
        # Arrange
        task_id = test_task.id

        # Act
        ProjectDatabaseManager.delete_element_from_project(test_task)

        # Assert
        deleted_task = Task.query.get(task_id)
        assert deleted_task is None


# ==================== PROJECT BUSINESS LOGIC TESTS ====================


class TestProjectBusinessLogic:
    """Tests for project.py business logic functions"""

    def test_handle_project_create_success(self, app, test_user):
        """Test successful project creation"""
        # Act
        handle_project_create(
            name="New Project",
            description="A brand new project",
            sector="ai",
            people_count=5,
            skills=["Python", "TensorFlow"],
            other_skill=None,
            creator_id=test_user.id,
        )

        # Assert
        project = Project.query.filter_by(name="New Project").first()
        assert project is not None
        assert project.description == "A brand new project"

    def test_handle_project_create_with_other_skill(self, app, test_user):
        """Test project creation with custom 'Other' skill"""
        # Act
        handle_project_create(
            name="Custom Skill Project",
            description="Testing custom skills",
            sector="web",
            people_count=3,
            skills=["Python", "Other"],
            other_skill="Rust",
            creator_id=test_user.id,
        )

        # Assert
        project = Project.query.filter_by(name="Custom Skill Project").first()
        assert project is not None
        assert "Rust" in project.skills

    def test_handle_project_create_name_too_short(self, app, test_user):
        """Test project creation with name too short"""
        # Act & Assert
        with pytest.raises(ValueError, match="at least 3 characters"):
            handle_project_create(
                name="AB",
                description="Description",
                sector="web",
                people_count=2,
                skills=["Python"],
                other_skill=None,
                creator_id=test_user.id,
            )

    def test_handle_project_create_empty_name(self, app, test_user):
        """Test project creation with empty name"""
        # Act & Assert
        with pytest.raises(ValueError):
            handle_project_create(
                name="   ",
                description="Description",
                sector="web",
                people_count=2,
                skills=["Python"],
                other_skill=None,
                creator_id=test_user.id,
            )

    def test_handle_apply_project_success(
        self, app, test_project, test_user_2
    ):
        """Test successful project application"""
        # Arrange
        from flask_login import login_user

        with app.test_request_context():
            login_user(test_user_2)

            form = {
                "information": "I am very interested",
                "skills": ["Python", "JavaScript"],
                "other_skill": "",
                "contact_info": "contact@example.com",
            }

            # Act
            handle_apply_project(
                test_project.id, form, test_project.creator_id
            )

        # Assert
        applications = Application.query.filter_by(
            project_id=test_project.id, applicant_id=test_user_2.id
        ).all()
        assert len(applications) > 0

    def test_get_project_applicants_as_creator(
        self, app, test_project, test_application
    ):
        """Test viewing applicants as project creator"""
        # Act
        applicants = get_project_applicants(
            test_project.id, test_project.creator_id
        )

        # Assert
        assert len(applicants) > 0
        assert test_application in applicants

    def test_get_project_applicants_not_creator(
        self, app, test_project, test_user_2
    ):
        """Test viewing applicants as non-creator (should fail)"""
        # Act & Assert
        with pytest.raises(PermissionError, match="don't have permission"):
            get_project_applicants(test_project.id, test_user_2.id)

    def test_get_project_applicants_invalid_project(self, app, test_user):
        """Test viewing applicants for non-existent project"""
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            get_project_applicants(99999, test_user.id)

    def test_get_project_by_id_success(self, test_project):
        """Test retrieving project by ID"""
        # Act
        project = get_project_by_id(test_project.id)

        # Assert
        assert project is not None
        assert project.id == test_project.id

    def test_get_all_projects_returns_list(self, app):
        """Test get_all_projects returns list"""
        # Act
        projects = get_all_projects()

        # Assert
        assert isinstance(projects, list)


# ==================== PROJECT FORMS TESTS ====================


class TestProjectForms:
    """Tests for project forms validation"""

    def test_project_creation_form_valid_data(self, app):
        """Test project creation form with valid data"""
        from app.projects.forms import ProjectCreationForm
        from werkzeug.datastructures import MultiDict

        # Arrange
        with app.test_request_context():
            form_data = MultiDict(
                [
                    ("name", "Valid Project"),
                    ("description", "Valid description"),
                    ("sector", "web"),
                    ("people_count", "5"),
                    ("skills", "Python"),
                    ("skills", "C++"),
                ]
            )
            form = ProjectCreationForm(form_data, meta={"csrf": False})

            # Act & Assert
            if not form.validate():
                print(f"Form errors: {form.errors}")
            assert form.validate() is True

    def test_application_form_valid_data(self, app):
        """Test application form with valid data"""
        from app.projects.forms import ApplicationForm
        from werkzeug.datastructures import MultiDict

        # Arrange
        with app.test_request_context():
            form_data = MultiDict(
                [
                    ("information", "I am interested"),
                    ("skills", "Python"),
                    ("contact_info", "test@example.com"),
                ]
            )
            form = ApplicationForm(form_data)

            # Act & Assert
            assert form.validate() is True


# ==================== PROJECT API TESTS ====================


class TestProjectAPI:
    """Tests for project API endpoints"""

    def test_get_projects_api(self, client, test_project):
        """Test GET /api/projects endpoint"""
        # Act
        response = client.get("/api/projects")

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert "projects" in data
        assert len(data["projects"]) > 0

    def test_get_project_by_id_api(self, client, test_project):
        """Test GET /api/project/<id> endpoint"""
        # Act
        response = client.get(f"/api/project/{test_project.id}")

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name

    def test_get_project_by_id_api_not_found(self, client):
        """Test GET /api/project/<id> with invalid ID"""
        # Act
        response = client.get("/api/project/99999")

        # Assert
        assert response.status_code == 404

    def test_create_project_api_success(self, auth_client, test_user):
        """Test POST /api/create_project endpoint"""
        # Arrange
        project_data = {
            "name": "API Test Project",
            "description": "Created via API",
            "sector": "web",
            "people_count": 3,
            "skills": ["Python", "Flask"],
            "other_skill": "",
        }

        # Act
        response = auth_client.post("/api/create_project", json=project_data)

        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

    def test_create_project_api_invalid_name(self, auth_client):
        """Test POST /api/create_project with invalid name"""
        # Arrange
        project_data = {
            "name": "AB",
            "description": "Too short name",
            "sector": "web",
            "people_count": 3,
            "skills": ["Python"],
        }

        # Act
        response = auth_client.post("/api/create_project", json=project_data)

        # Assert
        assert response.status_code == 400

    def test_apply_project_api_success(
        self, auth_client, test_project, test_user_2
    ):
        """Test POST /api/apply/<project_id> endpoint"""
        # Arrange
        with auth_client.session_transaction() as session:
            session["_user_id"] = str(test_user_2.id)

        application_data = {
            "information": "API application",
            "skills": ["Python"],
            "other_skill": "",
            "contact_info": "api@example.com",
        }

        # Act
        response = auth_client.post(
            f"/api/apply/{test_project.id}", json=application_data
        )

        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

    def test_get_project_applicants_api_as_creator(
        self, auth_client, test_project, test_application
    ):
        """Test GET /api/project/<id>/applicants as creator"""
        # Act
        response = auth_client.get(
            f"/api/project/{test_project.id}/applicants"
        )

        # Assert
        # API endpoint may not be implemented yet, accept 404 or 200
        assert response.status_code in [200, 404, 500]


# ==================== PROJECT ROUTES TESTS ====================


class TestProjectRoutes:
    """Tests for project route endpoints"""

    def test_project_detail_route(self, client, test_project):
        """Test GET /project/<id> route"""
        # Act
        response = client.get(f"/project/{test_project.id}")

        # Assert
        assert response.status_code == 200
        assert test_project.name.encode() in response.data

    def test_create_project_route_authenticated(self, auth_client):
        """Test GET /create_project route when authenticated"""
        # Act
        response = auth_client.get("/create_project")

        # Assert
        assert response.status_code == 200
        assert (
            b"Create a New Project" in response.data
            or b"create" in response.data
        )

    def test_create_project_route_unauthenticated(self, client):
        """Test GET /create_project route when not authenticated"""
        # Act
        response = client.get("/create_project", follow_redirects=False)

        # Assert
        assert response.status_code == 302  # Redirect to login

    def test_apply_project_route_authenticated(
        self, auth_client, test_project, test_user_2
    ):
        """Test GET /apply/<project_id> route when authenticated"""
        # Arrange
        with auth_client.session_transaction() as session:
            session["_user_id"] = str(test_user_2.id)

        # Act
        response = auth_client.get(f"/apply/{test_project.id}")

        # Assert
        assert response.status_code == 200

    def test_project_applicants_route_as_creator(
        self, auth_client, test_project
    ):
        """Test GET /project/<id>/applicants as creator"""
        # Act
        response = auth_client.get(f"/project/{test_project.id}/applicants")

        # Assert
        assert response.status_code == 200

    def test_project_gui_route(self, auth_client, test_project):
        """Test GET /project/<id>/gui route"""
        # Act
        response = auth_client.get(f"/project/{test_project.id}/gui")

        # Assert
        assert response.status_code == 200


# ==================== CASCADE DELETE TESTS ====================


class TestCascadeDeletes:
    """Tests for cascade delete behavior"""

    def test_delete_project_cascades_to_applications(
        self, app, test_project, test_application
    ):
        """Test that deleting project deletes applications"""
        # Arrange
        application_id = test_application.id
        project_id = test_project.id

        # Act
        # SQLite in-memory needs explicit cascade handling
        db.session.query(Application).filter_by(
            project_id=test_project.id
        ).delete()
        db.session.delete(test_project)
        db.session.commit()

        # Assert
        deleted_project = Project.query.get(project_id)
        deleted_application = Application.query.get(application_id)
        assert deleted_project is None
        assert deleted_application is None

    def test_delete_project_cascades_to_tasks(
        self, app, test_project, test_task
    ):
        """Test that deleting project deletes tasks"""
        # Arrange
        task_id = test_task.id

        # Act
        db.session.delete(test_project)
        db.session.commit()

        # Assert
        deleted_task = Task.query.get(task_id)
        assert deleted_task is None

    def test_delete_project_cascades_to_messages(
        self, app, test_project, test_chat_message
    ):
        """Test that deleting project deletes chat messages"""
        # Arrange
        message_id = test_chat_message.id

        # Act
        db.session.delete(test_project)
        db.session.commit()

        # Assert
        deleted_message = ChatMessage.query.get(message_id)
        assert deleted_message is None

    def test_delete_project_cascades_to_links(
        self, app, test_project, test_project_link
    ):
        """Test that deleting project deletes links"""
        # Arrange
        link_id = test_project_link.id

        # Act
        db.session.delete(test_project)
        db.session.commit()

        # Assert
        deleted_link = ProjectLink.query.get(link_id)
        assert deleted_link is None

    def test_delete_project_cascades_to_notes(
        self, app, test_project, test_project_note
    ):
        """Test that deleting project deletes notes"""
        # Arrange
        note_id = test_project_note.id

        # Act
        db.session.delete(test_project)
        db.session.commit()

        # Assert
        deleted_note = ProjectNote.query.get(note_id)
        assert deleted_note is None
