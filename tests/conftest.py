"""Pytest configuration and shared fixtures for testing."""
import pytest
from app import create_app
from app.extensions import db
from app.auth.models import User
# Import all models to ensure relationships work
from app.profile.models import Demo, UserSkill, Skill
from app.projects.models import Project


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    import os
    # Set test environment variables to avoid S3 errors
    os.environ.setdefault('S3_BUCKET', 'test-bucket')
    os.environ.setdefault('AWS_REGION', 'us-east-1')
    os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test-key')
    os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test-secret')
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create a sample user in the database for testing."""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Ensure ID is loaded
        return user


@pytest.fixture
def authenticated_client(client, sample_user):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(sample_user.id)
        sess['_fresh'] = True
    return client
