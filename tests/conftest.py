"""
Shared fixtures and configuration for pytest tests.
"""

import pytest
import os
from app import create_app
from app.extensions import db as _db
from app.profile.models import Skill, UserSkill
from app.auth.models import User

# Set environment variable BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def app():
    """Create application for testing with isolated SQLite database."""
    app = create_app()

    # Force override the database URI to SQLite in-memory
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SERVER_NAME"] = "localhost"
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["LOGIN_DISABLED"] = False

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
    """Create a test client."""
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
def test_user2(app, db):
    """Create a second test user."""
    user = User(username="testuser2", email="test2@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture(scope="function")
def other_user(app, db):
    """Alias for test_user2."""
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
