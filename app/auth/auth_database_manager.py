from .models import User
from app.extensions import db


class AuthDatabaseManager:
    @staticmethod
    def create_user(username, email, password):
        """Creates a new user in the database."""
        # Check if user already exists
        if AuthDatabaseManager.get_user_by_username(username):
            return None
        # Create a new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_username(username):
        """Fetches a user by username."""
        return User.query.filter_by(username=username).first()
