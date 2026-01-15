"""
Shared test fixtures and configuration for pytest.
"""

import os
import pytest
from app import create_app
from app.extensions import db as _db
from app.auth.models import User
from app.profile.models import Skill, UserSkill
from app.projects.models import (
    Project,
    Application,
    Task,
    ChatMessage,
    ProjectLink,
    ProjectNote,
)

# Set environment variables BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")


@pytest.fixture(scope="function")
def app():
    """Create and configure a test Flask application instance."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "SERVER_NAME": "localhost",
        "LOGIN_DISABLED": False,
    }

    app = create_app(config=test_config)

    with app.app_context():
        # Drop all tables first to ensure clean state
        _db.drop_all()
        _db.create_all()

        yield app

        # Cleanup
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide the database instance."""
    with app.app_context():
        yield _db


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def test_user(app, db):
    """Create a test user."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_2(app, db):
    """Create a second test user."""
    user = User(username="testuser2", email="test2@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)
    return client


@pytest.fixture(scope="function")
def test_project(app, db, test_user):
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
    db.session.refresh(project)
    return project


@pytest.fixture(scope="function")
def test_application(app, db, test_project, test_user_2):
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
    db.session.refresh(application)
    return application


@pytest.fixture(scope="function")
def test_task(app, db, test_project):
    """Create a test task."""
    task = Task(project_id=test_project.id, title="Test Task", is_done=False)
    db.session.add(task)
    db.session.commit()
    db.session.refresh(task)
    return task


@pytest.fixture(scope="function")
def test_chat_message(app, db, test_project, test_user):
    """Create a test chat message."""
    message = ChatMessage(
        project_id=test_project.id, author_id=test_user.id, body="Test message"
    )
    db.session.add(message)
    db.session.commit()
    db.session.refresh(message)
    return message


@pytest.fixture(scope="function")
def test_project_link(app, db, test_project):
    """Create a test project link."""
    link = ProjectLink(
        project_id=test_project.id,
        label="GitHub",
        url="https://github.com/test/repo",
    )
    db.session.add(link)
    db.session.commit()
    db.session.refresh(link)
    return link


@pytest.fixture(scope="function")
def test_project_note(app, db, test_project, test_user):
    """Create a test project note."""
    note = ProjectNote(
        project_id=test_project.id,
        author_id=test_user.id,
        content="Test note content",
    )
    db.session.add(note)
    db.session.commit()
    db.session.refresh(note)
    return note


@pytest.fixture(scope="function")
def other_user(app, db):
    """Create another test user."""
    user = User(username="otheruser", email="other@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_skill(app, db):
    """Create a test skill."""
    skill = Skill(name="Python")
    db.session.add(skill)
    db.session.commit()
    db.session.refresh(skill)
    return skill


@pytest.fixture(scope="function")
def test_user_skill(app, db, test_user, test_skill):
    """Create a test user skill."""
    user_skill = UserSkill(
        user_id=test_user.id,
        skill_id=test_skill.id,
        level="Intermediate",
        years=3,
    )
    db.session.add(user_skill)
    db.session.commit()
    db.session.refresh(user_skill)
    return user_skill


@pytest.fixture(scope="function")
def authenticated_client(app, client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)
        session["_fresh"] = True
    return client


# Aliases for backwards compatibility
@pytest.fixture(scope="function")
def user(test_user):
    """Alias for test_user."""
    return test_user


@pytest.fixture(scope="function")
def skill(test_skill):
    """Alias for test_skill."""
    return test_skill


@pytest.fixture(scope="function")
def sample_user(app, db):
    """Create a sample user for auth tests (alias for test_user with different password)."""
    user = User(username="sampleuser", email="sample@example.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user
