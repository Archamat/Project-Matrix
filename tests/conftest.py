"""
Shared test fixtures and configuration for pytest.
"""

import pytest
from app import create_app
from app.extensions import db
from app.auth.models import User
from app.projects.models import (
    Project,
    Application,
    Task,
    ChatMessage,
    ProjectLink,
    ProjectNote,
)


@pytest.fixture(scope="function")
def app():
    """Create and configure a test Flask application instance."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    }

    app = create_app(config=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def test_user(app):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
    )
    user.set_password("TestPass123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_user_2(app):
    """Create a second test user."""
    user = User(
        username="testuser2",
        email="test2@example.com",
    )
    user.set_password("TestPass123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def auth_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)
    return client


@pytest.fixture(scope="function")
def test_project(app, test_user):
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="A test project for testing purposes",
        sector="web",
        people_count=5,
        skills="Python, JavaScript, HTML",
        creator=test_user,
    )
    db.session.add(project)
    db.session.commit()
    return project


@pytest.fixture(scope="function")
def test_application(app, test_project, test_user_2):
    """Create a test application."""
    application = Application(
        project_id=test_project.id,
        applicant_id=test_user_2.id,
        information="I am interested in this project",
        skills="Python, JavaScript",
        contact_info="test2@example.com",
    )
    db.session.add(application)
    db.session.commit()
    return application


@pytest.fixture(scope="function")
def test_task(app, test_project):
    """Create a test task."""
    task = Task(project_id=test_project.id, title="Test Task", is_done=False)
    db.session.add(task)
    db.session.commit()
    return task


@pytest.fixture(scope="function")
def test_chat_message(app, test_project, test_user):
    """Create a test chat message."""
    message = ChatMessage(
        project_id=test_project.id, author_id=test_user.id, body="Test message"
    )
    db.session.add(message)
    db.session.commit()
    return message


@pytest.fixture(scope="function")
def test_project_link(app, test_project):
    """Create a test project link."""
    link = ProjectLink(
        project_id=test_project.id,
        label="GitHub",
        url="https://github.com/test/repo",
    )
    db.session.add(link)
    db.session.commit()
    return link


@pytest.fixture(scope="function")
def test_project_note(app, test_project, test_user):
    """Create a test project note."""
    note = ProjectNote(
        project_id=test_project.id,
        author_id=test_user.id,
        content="Test note content",
    )
    db.session.add(note)
    db.session.commit()
    return note
