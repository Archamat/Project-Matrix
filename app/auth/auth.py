from flask import redirect, url_for, flash
from flask_login import login_user, logout_user
from .auth_database_manager import AuthDatabaseManager


# Login route logic
def handle_login(data):
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return {'success': False, 'error': 'Username and password required'}

    user = AuthDatabaseManager.get_user_by_username(username)
    if user and user.check_password(password):
        login_user(user)
        return {'success': True, 'message': 'Login successful'}
    else:
        return {'success': False, 'error': 'Invalid username or password'}


def handle_register(data):
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password or not email:
        return {'success': False, 'error': 'All fields are required'}

    user = AuthDatabaseManager.create_user(username, email, password)
    if not user:
        return {'success': False, 'error': 'User already exists'}

    return {'success': True, 'message': 'Registration successful'}


def handle_logout():
    try:
        logout_user()
        return {'success': True, 'message': 'Logged out successfully'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
