from flask_login import login_user, logout_user
from .auth_database_manager import AuthDatabaseManager


# Login route logic
def handle_login(data):
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        raise ValueError('Username and password are required')

    user = AuthDatabaseManager.get_user_by_username(username)
    if user and user.check_password(password):
        try:
            login_user(user)
            return True
        except Exception as e:
            raise ValueError(f"Login failed: {str(e)}")
    else:
        raise ValueError('Invalid username or password')


def handle_register(data):
    try:
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        if not username or not password or not email:
            raise ValueError('Username, password, and email are required')
        user = AuthDatabaseManager.create_user(username, email, password)
        if not user:
            raise ValueError('An error occurred during registration')
    except Exception as e:
        raise ValueError(f"Registration failed: {str(e)}")


def handle_logout():
    try:
        logout_user()
        return {'success': True, 'message': 'Logged out successfully'}
    except Exception as e:
        raise ValueError(f"Logout failed: {str(e)}")
