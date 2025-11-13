from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth.models import User
from app.profile.profile import handle_profile
from app.profile.profile_database_manager import ProfileDatabaseManager
from app.aws import upload_fileobj_private
from app.aws.s3 import presigned_get_url

# Constants
AUDIO_MIME_ALLOW = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/webm",
    "audio/x-wav", "audio/wave", "audio/flac"
}
IMAGE_MIME_ALLOW = {"image/jpeg", "image/png", "image/webp", "image/gif"}


profile = Blueprint('profile', __name__)

# ==================== VIEW ROUTES (Render Templates) ====================

@profile.route('/profile')
@login_required
def show_profile():
    """Show current user's profile"""
    profile_data = handle_profile(current_user)
    return render_template('profile.html',
                          user=profile_data['user'],
                          demos=profile_data['demos'],
                          is_owner=True,
                          current_page='profile')


@profile.get("/u/<string:username>")
@login_required
def view_profile(username):
    """View another user's public profile"""
    user = User.query.filter_by(username=username).first_or_404()
    is_owner = (user.id == current_user.id)
    
    profile_data = handle_profile(user)
    return render_template('profile.html',
                          user=profile_data['user'],
                          demos=profile_data['demos'],
                          is_owner=is_owner,
                          current_page='profile')


# ==================== TRADITIONAL FORM HANDLERS (for backward compatibility) ====================

@profile.route('/profile/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Traditional form handler for avatar upload"""
    file = request.files.get("avatar_file")

    if not file or file.filename == "":
        flash("Please choose an image file.", "warning")
        return redirect(url_for("profile.show_profile"))

    if file.mimetype not in IMAGE_MIME_ALLOW:
        flash("Only JPG/PNG/WEBP/GIF allowed.", "danger")
        return redirect(url_for("profile.show_profile"))

    try:
        result = upload_fileobj_private(file, prefix=f"avatars/{current_user.id}/")
        current_user.avatar_url = result["key"]
        from app.extensions import db
        db.session.commit()
        flash("Avatar updated!", "success")
    except Exception as e:
        flash(f"Upload failed: {e}", "danger")

    return redirect(url_for("profile.show_profile"))


@profile.route('/profile/update', methods=['POST'])
@login_required
def update_profile_info():
    """Traditional form handler for profile update"""
    from app.profile.profile import handle_update_profile

    try:
        data = request.form.to_dict()
        handle_update_profile(current_user, data)
        flash('Profile updated successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception:
        flash('An error occurred while updating your profile.', 'error')

    return redirect(url_for('profile.show_profile'))


@profile.post("/profile/upload_demo")
@login_required
def upload_demo():
    """Traditional form handler for demo upload"""
    from app.profile.profile import handle_demo_upload

    file = request.files.get("demo_file")
    title = request.form.get("title", "").strip()

    if not file or file.filename == "":
        flash("Please choose an audio file.", "warning")
        return redirect(url_for("profile.show_profile"))

    if file.mimetype not in AUDIO_MIME_ALLOW:
        flash("Unsupported audio type.", "danger")
        return redirect(url_for("profile.show_profile"))

    try:
        result = upload_fileobj_private(file, prefix=f"demos/{current_user.id}/")
        handle_demo_upload(current_user, result["key"], title or file.filename, file.mimetype)
        flash("Demo uploaded!", "success")
    except Exception as e:
        flash(f"Upload failed: {e}", "danger")

    return redirect(url_for("profile.show_profile"))


@profile.post("/profile/delete_demo/<int:demo_id>")
@login_required
def delete_demo(demo_id):
    """Traditional form handler for demo deletion"""
    from app.profile.profile import handle_demo_delete

    try:
        handle_demo_delete(current_user, demo_id)
        flash("Demo removed.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception:
        flash("Failed to delete demo.", "error")

    return redirect(url_for("profile.show_profile"))


@profile.get("/profile/demos")
@login_required
def list_demos():
    """Render all demos page"""
    demos = ProfileDatabaseManager.get_user_demos(current_user.id)

    items = []
    for d in demos:
        try:
            url = presigned_get_url(d.key, expires_in=3600)
        except Exception:
            url = None
        items.append({
            "id": d.id,
            "title": d.title,
            "mime": d.mime,
            "url": url,
            "updated_at": d.updated_at
        })

    return render_template("partials/_demos_list.html", items=items)


@profile.post("/profile/skills/add")
@login_required
def add_skill():
    """Traditional form handler for adding skill"""
    from app.profile.profile import handle_skill_add

    skill_name = request.form.get("instrument", "").strip()
    level = request.form.get("level")
    years = request.form.get("years", 0)

    try:
        handle_skill_add(current_user, skill_name, level, years)
        flash(f"Added skill: {skill_name}", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Failed to add skill.", "error")

    return redirect(url_for("profile.show_profile"))


@profile.post("/profile/skills/delete/<int:user_skill_id>")
@login_required
def delete_skill(user_skill_id):
    """Traditional form handler for removing skill"""
    from app.profile.profile import handle_skill_delete

    try:
        handle_skill_delete(current_user, user_skill_id)
        flash("Skill removed.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception:
        flash("Failed to remove skill.", "error")

    return redirect(url_for("profile.show_profile"))
