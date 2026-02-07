"""
Shared fixtures and configuration for pytest tests.
"""

import os
import pytest
from app import create_app
from app.extensions import db as _db
from app.auth.models import User
from app.profile.models import Skill, UserSkill, Demo
from app.projects.models import (
    Project,
    Application,
    Task,
    ChatMessage,
    ProjectLink,
    ProjectNote,
)

# Set environment variables for testing
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
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
        _db.create_all()
        yield app
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
    """Create a test CLI runner for the Flask application."""
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
def sample_user(app, db):
    """Create a sample user in the database for testing."""
    existing_user = User.query.filter_by(username="testuser").first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()

    user = User(username="testuser", email="test@example.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)
        session["_fresh"] = True
    return client


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
    return application


@pytest.fixture(scope="function")
def test_task(app, db, test_project):
    """Create a test task."""
    task = Task(project_id=test_project.id, title="Test Task", is_done=False)
    db.session.add(task)
    db.session.commit()
    return task


@pytest.fixture(scope="function")
def test_chat_message(app, db, test_project, test_user):
    """Create a test chat message."""
    message = ChatMessage(
        project_id=test_project.id, author_id=test_user.id, body="Test message"
    )
    db.session.add(message)
    db.session.commit()
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
    return note


# Aliases for backwards compatibility
@pytest.fixture(scope="function")
def user(test_user):
    """Alias for test_user."""
    return test_user


@pytest.fixture(scope="function")
def skill(test_skill):
    """Alias for test_skill."""
    return test_skill