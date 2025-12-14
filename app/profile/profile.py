from app.aws.s3 import presigned_get_url
from app.profile.profile_database_manager import ProfileDatabaseManager


def handle_profile(user):
    """
    Prepare profile data for display.
    Returns dict with user info, demos with presigned URLs, etc.
    """
    # Get user's demos with presigned URLs
    demos = []
    for demo in ProfileDatabaseManager.get_user_demos(user.id):
        # Generate presigned URL
        try:
            url = presigned_get_url(demo.key, expires_in=3600)
        except Exception:
            url = None

        demos.append(demo.to_dict(include_url=True, presigned_url=url))

    return {"user": user, "demos": demos}


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


def handle_demo_upload(user, s3_key, title, mime_type):
    """Business logic for demo upload"""
    if not s3_key or not mime_type:
        raise ValueError("Invalid demo data")

    # Sanitize title
    title = (title or "Untitled").strip()

    return ProfileDatabaseManager.create_demo(user.id, s3_key, title, mime_type)


def handle_demo_delete(user, demo_id):
    """Business logic for demo deletion"""
    demo = ProfileDatabaseManager.get_demo_by_id(demo_id, user.id)
    if not demo:
        raise ValueError("Demo not found or unauthorized")

    ProfileDatabaseManager.delete_demo(demo)
    return True


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
        if years < 0 or years > 50:
            raise ValueError("Years must be between 0 and 50")
    except (ValueError, TypeError):
        raise ValueError("Invalid years value")

    return ProfileDatabaseManager.add_user_skill(user.id, skill_name, level, years)


def handle_skill_delete(user, user_skill_id):
    """Business logic for removing a skill"""
    user_skill = ProfileDatabaseManager.get_user_skill(user_skill_id, user.id)
    if not user_skill:
        raise ValueError("Skill not found or unauthorized")

    ProfileDatabaseManager.delete_user_skill(user_skill)
    return True
