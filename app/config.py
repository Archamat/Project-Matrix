import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'test')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://project_app:test@localhost/project_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

