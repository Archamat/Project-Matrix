from flask import render_template, request
from app.projects.models import Project
from app.filter.filter import get_filter_data, filter_projects
from flask_login import current_user


def handle_dashboard():
    # Get filter options for the dropdown
    options = []
    filter_data = get_filter_data()

    # Check if user applied filters
    selected_sectors = request.args.getlist('sectors')
    selected_num_of_people = request.args.getlist('people_counts')
    selected_skills = request.args.getlist('skills')
    # Get filtered projects
    if selected_sectors and selected_sectors != ['all']:
        options.append(('sectors', selected_sectors))
    if selected_num_of_people and selected_num_of_people != ['all']:
        options.append(('people_count', selected_num_of_people))
    if selected_skills and selected_skills != ['all']:
        options.append(('skills', selected_skills))
    if options:
        projects = filter_projects(dict(options))
    else:
        projects = Project.query.order_by(Project.id.desc()).limit(10).all()

    # Get user's created projects if authenticated
    user_projects = []
    if current_user.is_authenticated:
        user_projects = Project.query.filter_by(
            creator_id=current_user.id).all()

    return render_template('dashboard.html',
                           projects=projects,
                           user_projects=user_projects,
                           filter_data=filter_data,
                           current_sectors=selected_sectors,
                           current_num_of_people=selected_num_of_people,
                           current_skills=selected_skills)
