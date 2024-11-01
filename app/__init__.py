from flask import Flask
from .extensions import db, login_manager
from .config import Config
from app.auth.models import User
from app.auth.routes import auth
from app.main.routes import main
from app.profile.routes import profile
from app.projects.routes import project
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(profile)
    app.register_blueprint(project)
    # Shell context processor
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}  # Expose db and User model

    migrate = Migrate(app, db)
    return app


