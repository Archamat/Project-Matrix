"""
Shared test fixtures and configuration for pytest.

Unified test infrastructure combining:
- PR #26: Project module tests (project/application/task/chat/link/note fixtures)
- PR #27: Auth module tests (sample_user, login fixtures)
- PR #28: Profile module tests (skill fixtures, db fixture, authenticated_client)
"""

import os
import pytest
from app import create_app
from app.extensions import db as _db
from app.auth.models import User
from app.projects.models import (
    Project,
    Application,
    Task,
    ChatMessage,
    ProjectLink,
    ProjectNote,
)
from app.profile.models import Demo, Skill, UserSkill  # noqa: F401

# Set environment variables BEFORE app creation to avoid S3/DB errors
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")


# ==================== APP & CLIENT FIXTURES ====================


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
        _db.drop_all()
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
    """Create a test CLI runner."""
    return app.test_cli_runner()


# ==================== USER FIXTURES ====================


@pytest.fixture(scope="function")
def test_user(app):
    """Create a test user (used by project and profile tests)."""
    user = User(
        username="testuser",
        email="test@example.com",
    )
    user.set_password("TestPass123!")
    _db.session.add(user)
    _db.session.commit()
    _db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_2(app):
    """Create a second test user (used by project tests)."""
    user = User(
        username="testuser2",
        email="test2@example.com",
    )
    user.set_password("TestPass123!")
    _db.session.add(user)
    _db.session.commit()
    _db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user2(app):
    """Create a second test user (used by profile tests)."""
    user = User(
        username="testuser2",
        email="test2@example.com",
    )
    user.set_password("password123")
    _db.session.add(user)
    _db.session.commit()
    _db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def other_user(app):
    """Create a third test user with a different username."""
    user = User(
        username="otheruser",
        email="other@example.com",
    )
    user.set_password("password123")
    _db.session.add(user)
    _db.session.commit()
    _db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_user(app):
    """Create a sample user for auth tests (password: testpass123)."""
    with app.app_context():
        existing_user = User.query.filter_by(username="testuser").first()
        if existing_user:
            _db.session.delete(existing_user)
            _db.session.commit()

        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass123")
        _db.session.add(user)
        _db.session.commit()
        _db.session.refresh(user)
        return user


# ==================== AUTH FIXTURES ====================


@pytest.fixture(scope="function")
def auth_client(client, test_user):
    """Create an authenticated test client (used by project tests)."""
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)
    return client


@pytest.fixture(scope="function")
def authenticated_client(app, client, test_user):
    """Create an authenticated test client with fresh session (used by profile tests)."""
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)
        session["_fresh"] = True
    return client


# ==================== PROJECT FIXTURES (PR #26) ====================


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
    _db.session.add(project)
    _db.session.commit()
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
    _db.session.add(application)
    _db.session.commit()
    return application


@pytest.fixture(scope="function")
def test_task(app, test_project):
    """Create a test task."""
    task = Task(project_id=test_project.id, title="Test Task", is_done=False)
    _db.session.add(task)
    _db.session.commit()
    return task


@pytest.fixture(scope="function")
def test_chat_message(app, test_project, test_user):
    """Create a test chat message."""
    message = ChatMessage(
        project_id=test_project.id, author_id=test_user.id, body="Test message"
    )
    _db.session.add(message)
    _db.session.commit()
    return message


@pytest.fixture(scope="function")
def test_project_link(app, test_project):
    """Create a test project link."""
    link = ProjectLink(
        project_id=test_project.id,
        label="GitHub",
        url="https://github.com/test/repo",
    )
    _db.session.add(link)
    _db.session.commit()
    return link


@pytest.fixture(scope="function")
def test_project_note(app, test_project, test_user):
    """Create a test project note."""
    note = ProjectNote(
        project_id=test_project.id,
        author_id=test_user.id,
        content="Test note content",
    )
    _db.session.add(note)
    _db.session.commit()
    return note


# ==================== SKILL FIXTURES (PR #28) ====================


@pytest.fixture(scope="function")
def test_skill(app):
    """Create a test skill."""
    skill = Skill(name="Python")
    _db.session.add(skill)
    _db.session.commit()
    _db.session.refresh(skill)
    return skill


@pytest.fixture(scope="function")
def test_user_skill(app, test_user, test_skill):
    """Create a test user skill."""
    user_skill = UserSkill(
        user_id=test_user.id,
        skill_id=test_skill.id,
        level="Intermediate",
        years=3,
    )
    _db.session.add(user_skill)
    _db.session.commit()
    _db.session.refresh(user_skill)
    return user_skill


# ==================== ALIASES ====================


@pytest.fixture(scope="function")
def user(test_user):
    """Alias for test_user."""
    return test_user


@pytest.fixture(scope="function")
def skill(test_skill):
    """Alias for test_skill."""
    return test_skill
