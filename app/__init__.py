from flask import Flask
from .extensions import db, login_manager
from .config import Config
from app.auth.models import User
from app.auth.routes import auth
from app.auth.api import auth_api
from app.main.routes import main
from app.dashboard.routes import dashboard
from app.profile.routes import profile
from app.profile.api import profile_api
from app.projects.routes import project
from app.projects.api import project_api
from flask_migrate import Migrate
from app.search import bp as search_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register web blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(profile)
    app.register_blueprint(project)
    app.register_blueprint(search_bp)
    app.register_blueprint(dashboard)

    # Register API blueprints
    app.register_blueprint(auth_api)
    app.register_blueprint(project_api)
    app.register_blueprint(profile_api)

    # Shell context processor
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User}  # Expose db and User model

    migrate = Migrate(app, db)
    return app


