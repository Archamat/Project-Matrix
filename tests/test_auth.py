"""Unit tests for the authentication module."""
import pytest
from flask import url_for
from app.auth.models import User
from app.auth import models as auth_models
from app.auth.auth import handle_login, handle_register, handle_logout
from app.auth.auth_database_manager import AuthDatabaseManager
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self, app):
        """Test creating a user with valid data."""
        with app.app_context():
            # Create user without relationships to avoid issues
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)  # Refresh to get the ID

            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password != 'password123'  # Should be hashed
            assert len(user.password) > 20  # Hashed password should be long

    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            assert user.password != 'password123'
            # Werkzeug may use different hash formats (pbkdf2, scrypt, etc.)
            # Just check that it's hashed (not plain text)
            assert len(user.password) > 20  # Hashed passwords are longer

    def test_password_checking(self, app):
        """Test password verification."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            assert user.check_password('password123') is True
            assert user.check_password('wrongpassword') is False

    def test_user_unique_username(self, app):
        """Test that usernames must be unique."""
        with app.app_context():
            user1 = User(username='testuser', email='test1@example.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()

            user2 = User(username='testuser', email='test2@example.com')
            user2.set_password('password123')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()

    def test_user_unique_email(self, app):
        """Test that emails must be unique."""
        with app.app_context():
            user1 = User(username='user1', email='test@example.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()

            user2 = User(username='user2', email='test@example.com')
            user2.set_password('password123')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()

    def test_avatar_presigned_property(self, app, monkeypatch):
        """Test avatar_presigned property."""
        # Mock presigned_get_url in the models module where it's used
        def mock_presigned_url(key, expires_in=3600):
            return f'https://presigned-url.com/{key}'
        
        # Patch the imported function in the models module
        monkeypatch.setattr(auth_models, 'presigned_get_url', mock_presigned_url)
        
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            user.avatar_url = 'avatars/test.jpg'
            db.session.add(user)
            db.session.commit()

            # Access the property
            presigned = user.avatar_presigned
            assert presigned is not None
            assert isinstance(presigned, str)
            assert 'avatars/test.jpg' in presigned or 'presigned-url.com' in presigned

    def test_avatar_presigned_none_when_no_url(self, app):
        """Test avatar_presigned returns None when no avatar_url."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            assert user.avatar_url is None
            assert user.avatar_presigned is None


class TestAuthDatabaseManager:
    """Tests for AuthDatabaseManager."""

    def test_create_user_success(self, app):
        """Test successful user creation."""
        with app.app_context():
            user = AuthDatabaseManager.create_user(
                username='newuser',
                email='newuser@example.com',
                password='password123'
            )
            
            assert user is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
            assert user.check_password('password123') is True

    def test_create_user_duplicate_username(self, app):
        """Test creating user with duplicate username returns None."""
        with app.app_context():
            # Create first user
            user1 = AuthDatabaseManager.create_user(
                username='testuser',
                email='test1@example.com',
                password='password123'
            )
            assert user1 is not None

            # Try to create duplicate
            user2 = AuthDatabaseManager.create_user(
                username='testuser',
                email='test2@example.com',
                password='password123'
            )
            assert user2 is None

    def test_get_user_by_username_exists(self, app):
        """Test getting user by username when user exists."""
        with app.app_context():
            AuthDatabaseManager.create_user(
                username='testuser',
                email='test@example.com',
                password='password123'
            )
            
            user = AuthDatabaseManager.get_user_by_username('testuser')
            assert user is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'

    def test_get_user_by_username_not_exists(self, app):
        """Test getting user by username when user doesn't exist."""
        with app.app_context():
            user = AuthDatabaseManager.get_user_by_username('nonexistent')
            assert user is None


class TestAuthHandlers:
    """Tests for auth handlers (handle_login, handle_register, handle_logout)."""

    def test_handle_login_success(self, app, sample_user):
        """Test successful login."""
        with app.test_request_context():
            data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            
            result = handle_login(data)
            assert result is True

    def test_handle_login_missing_username(self, app):
        """Test login with missing username raises ValueError."""
        with app.test_request_context():
            data = {'password': 'password123'}
            
            with pytest.raises(ValueError, match='Username and password are required'):
                handle_login(data)

    def test_handle_login_missing_password(self, app):
        """Test login with missing password raises ValueError."""
        with app.test_request_context():
            data = {'username': 'testuser'}
            
            with pytest.raises(ValueError, match='Username and password are required'):
                handle_login(data)

    def test_handle_login_invalid_username(self, app):
        """Test login with invalid username raises ValueError."""
        with app.test_request_context():
            data = {
                'username': 'nonexistent',
                'password': 'password123'
            }
            
            with pytest.raises(ValueError, match='Invalid username or password'):
                handle_login(data)

    def test_handle_login_invalid_password(self, app, sample_user):
        """Test login with invalid password raises ValueError."""
        with app.test_request_context():
            data = {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
            
            with pytest.raises(ValueError, match='Invalid username or password'):
                handle_login(data)

    def test_handle_register_success(self, app):
        """Test successful registration."""
        with app.app_context():
            data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123'
            }
            
            handle_register(data)
            
            # Verify user was created
            user = AuthDatabaseManager.get_user_by_username('newuser')
            assert user is not None
            assert user.email == 'newuser@example.com'

    def test_handle_register_missing_username(self, app):
        """Test registration with missing username raises ValueError."""
        with app.app_context():
            data = {
                'email': 'test@example.com',
                'password': 'password123'
            }
            
            with pytest.raises(ValueError, match='Username, password, and email are required'):
                handle_register(data)

    def test_handle_register_missing_email(self, app):
        """Test registration with missing email raises ValueError."""
        with app.app_context():
            data = {
                'username': 'testuser',
                'password': 'password123'
            }
            
            with pytest.raises(ValueError, match='Username, password, and email are required'):
                handle_register(data)

    def test_handle_register_missing_password(self, app):
        """Test registration with missing password raises ValueError."""
        with app.app_context():
            data = {
                'username': 'testuser',
                'email': 'test@example.com'
            }
            
            with pytest.raises(ValueError, match='Username, password, and email are required'):
                handle_register(data)

    def test_handle_register_duplicate_username(self, app, sample_user):
        """Test registration with duplicate username raises ValueError."""
        with app.app_context():
            data = {
                'username': 'testuser',  # Already exists
                'email': 'different@example.com',
                'password': 'password123'
            }
            
            with pytest.raises(ValueError, match='Username already exists'):
                handle_register(data)

    def test_handle_logout_success(self, app):
        """Test successful logout."""
        with app.test_request_context():
            result = handle_logout()
            assert result['success'] is True
            assert 'message' in result


class TestAuthAPI:
    """Tests for auth API endpoints."""

    def test_api_login_success(self, client, sample_user):
        """Test successful login via API."""
        response = client.post(
            '/api/login',
            json={
                'username': 'testuser',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data

    def test_api_login_missing_data(self, client):
        """Test login API with missing data."""
        response = client.post(
            '/api/login',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_api_login_invalid_credentials(self, client):
        """Test login API with invalid credentials."""
        response = client.post(
            '/api/login',
            json={
                'username': 'nonexistent',
                'password': 'wrongpass'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_api_register_success(self, client, app):
        """Test successful registration via API."""
        with app.app_context():
            response = client.post(
                '/api/register',
                json={
                    'username': 'newuser',
                    'email': 'newuser@example.com',
                    'password': 'password123'
                },
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            assert 'message' in data

    def test_api_register_missing_data(self, client):
        """Test registration API with missing data."""
        response = client.post(
            '/api/register',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_api_register_duplicate_username(self, client, sample_user):
        """Test registration API with duplicate username."""
        response = client.post(
            '/api/register',
            json={
                'username': 'testuser',  # Already exists
                'email': 'different@example.com',
                'password': 'password123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_api_logout_success(self, client):
        """Test successful logout via API."""
        response = client.post(
            '/api/logout',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data


class TestAuthRoutes:
    """Tests for auth route endpoints (GET routes)."""

    def test_login_route_get(self, client):
        """Test GET /login route."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'username' in response.data.lower()

    def test_register_route_get(self, client):
        """Test GET /register route."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'username' in response.data.lower()


class TestAuthForms:
    """Tests for auth forms validation."""

    def test_login_form_valid(self, app):
        """Test LoginForm with valid data."""
        with app.app_context():
            form = LoginForm(data={
                'username': 'testuser',
                'password': 'password123'
            })
            assert form.validate() is True

    def test_login_form_missing_username(self, app):
        """Test LoginForm validation with missing username."""
        with app.app_context():
            form = LoginForm(data={'password': 'password123'})
            assert form.validate() is False
            assert 'username' in form.errors

    def test_login_form_missing_password(self, app):
        """Test LoginForm validation with missing password."""
        with app.app_context():
            form = LoginForm(data={'username': 'testuser'})
            assert form.validate() is False
            assert 'password' in form.errors

    def test_registration_form_valid(self, app):
        """Test RegistrationForm with valid data."""
        with app.app_context():
            form = RegistrationForm(data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            assert form.validate() is True

    def test_registration_form_missing_username(self, app):
        """Test RegistrationForm validation with missing username."""
        with app.app_context():
            form = RegistrationForm(data={
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            assert form.validate() is False
            assert 'username' in form.errors

    def test_registration_form_invalid_email(self, app):
        """Test RegistrationForm validation with invalid email."""
        with app.app_context():
            form = RegistrationForm(data={
                'username': 'testuser',
                'email': 'invalid-email',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            assert form.validate() is False
            assert 'email' in form.errors

    def test_registration_form_password_mismatch(self, app):
        """Test RegistrationForm validation with password mismatch."""
        with app.app_context():
            form = RegistrationForm(data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'differentpass'
            })
            assert form.validate() is False
            assert 'confirm_password' in form.errors
