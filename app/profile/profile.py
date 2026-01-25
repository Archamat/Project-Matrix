from app.profile.profile_database_manager import ProfileDatabaseManager


def handle_profile(user):
    """
    Prepare profile data for display.
    Returns dict with user info, participated projects, etc.
    """
    # Get projects the user has applied to (participated projects)
    # Also include projects the user created
    participated_projects = []
    project_ids = set()

    # Add projects from applications
    if hasattr(user, "applications"):
        for application in user.applications:
            if (
                application.project
                and application.project_id not in project_ids
            ):
                project_ids.add(application.project_id)
                participated_projects.append(application.project)

    # Add projects the user created
    if hasattr(user, "projects"):
        for project in user.projects:
            if project.id not in project_ids:
                project_ids.add(project.id)
                participated_projects.append(project)

    return {"user": user, "participated_projects": participated_projects}


def handle_update_profile(user, data):
    """Business logic for updating profile"""
    # Validate required fields
    if not data.get("username") or not data.get("email"):
        raise ValueError("Username and email are required")

    # Sanitize input
    sanitized_data = {
        "username": data.get("username", "").strip(),
        "email": data.get("email", "").strip(),
        "contact_info": data.get("contact_info", "").strip(),
        "bio": data.get("bio", "").strip(),
    }

    # Delegate to database manager
    return ProfileDatabaseManager.update_user_profile(user, sanitized_data)


def handle_avatar_upload(user, s3_key):
    """Business logic for avatar upload"""
    if not s3_key:
        raise ValueError("S3 key is required")

    return ProfileDatabaseManager.update_avatar(user, s3_key)


def handle_skill_add(user, skill_name, level, years):
    """Business logic for adding a skill"""
    # Validate input
    if not skill_name or not level:
        raise ValueError("Skill name and level are required")

    # Validate level
    valid_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
    if level not in valid_levels:
        raise ValueError(f'Level must be one of: {", ".join(valid_levels)}')

    # Validate years
    try:
        years = int(years)
    except (TypeError, ValueError):
        raise ValueError("Invalid years value")

    if years < 0 or years > 50:
        raise ValueError("Years must be between 0 and 50")

    return ProfileDatabaseManager.add_user_skill(
        user.id, skill_name, level, years
    )


def handle_skill_delete(user, user_skill_id):
    """Business logic for removing a skill"""
    user_skill = ProfileDatabaseManager.get_user_skill(user_skill_id, user.id)
    if not user_skill:
        raise ValueError("Skill not found or unauthorized")

    ProfileDatabaseManager.delete_user_skill(user_skill)
    return True
