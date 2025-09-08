from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .profile import handle_profile,update_profile
from app.extensions import db
from app.aws import upload_fileobj_private

profile = Blueprint('profile', __name__)

@profile.route('/profile')
@login_required

def show_profile():
    return handle_profile()

@profile.route('/profile/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    f = request.files.get("avatar_file")
    if not f or f.filename == "":
        flash("Please choose an image file.", "warning")
        return redirect(url_for("profile.show_profile"))

    if f.mimetype not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        flash("Only JPG/PNG/WEBP/GIF allowed.", "danger")
        return redirect(url_for("profile.show_profile"))

    try:
        result = upload_fileobj_private(f, prefix=f"avatars/{current_user.id}/")
        current_user.avatar_url = result["key"]   # <-- store KEY in DB
        db.session.commit()
        flash("Avatar updated!", "success")
    except Exception as e:
        flash(f"Upload failed: {e}", "danger")

    return redirect(url_for("profile.show_profile"))

@profile.route('/profile/update', methods=['POST'])
def update_profile_info():
    return update_profile()