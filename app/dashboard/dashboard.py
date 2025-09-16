from flask import render_template
from app.projects.models import Project
from flask_login import current_user

def handle_dashboard():
    # Get all available projects for the main feed
    projects = Project.query.order_by(Project.id.desc()).limit(10).all()
    
    # Get user's created projects if authenticated
    user_projects = []
    if current_user.is_authenticated:
        user_projects = Project.query.filter_by(creator_id=current_user.id).all()
    
    return render_template('dashboard.html', 
                         projects=projects, 
                         user_projects=user_projects)