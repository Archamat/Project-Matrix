from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .profile import handle_profile,update_profile
from app.extensions import db
from app.aws import upload_fileobj_private
from app.profile.models import Demo, Skill, UserSkill
from app.aws.s3 import presigned_get_url, s3_client, S3_BUCKET

# Constants
AUDIO_MIME_ALLOW = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/webm",
    "audio/x-wav", "audio/wave", "audio/flac"
}
IMAGE_MIME_ALLOW = {"image/jpeg", "image/png", "image/webp", "image/gif"}


profile = Blueprint('profile', __name__)

@profile.route('/profile')
@login_required

def show_profile():
    return handle_profile()

###Avatar Upload###
@profile.route('/profile/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    f = request.files.get("avatar_file")
    if not f or f.filename == "":
        flash("Please choose an image file.", "warning")
        return redirect(url_for("profile.show_profile"))

    if f.mimetype not in IMAGE_MIME_ALLOW:
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

###Demos###
@profile.post("/profile/upload_demo")
@login_required
def upload_demo():
    f = request.files.get("demo_file")
    title = (request.form.get("title") or "").strip()

    if not f or f.filename == "":
        flash("Please choose an audio file.", "warning")
        return redirect(url_for("profile.show_profile"))

    if f.mimetype not in AUDIO_MIME_ALLOW:
        flash("Unsupported audio type.", "danger")
        return redirect(url_for("profile.show_profile"))

    try:
        # Store under demos/{user_id}/...
        result = upload_fileobj_private(f, prefix=f"demos/{current_user.id}/")
        demo = Demo(
            user_id=current_user.id,
            key=result["key"],
            title=title or f.filename,
            mime=f.mimetype,
        )
        db.session.add(demo)
        db.session.commit()
        flash("Demo uploaded!", "success")
    except Exception as e:
        flash(f"Upload failed: {e}", "danger")

    return redirect(url_for("profile.show_profile"))

@profile.post("/profile/delete_demo/<int:demo_id>")
@login_required
def delete_demo(demo_id):
    demo = Demo.query.filter_by(id=demo_id, user_id=current_user.id).first_or_404()
    s3_client.delete_object(Bucket=S3_BUCKET, Key=demo.key)
    db.session.delete(demo)
    db.session.commit()
    flash("Demo removed.", "success")
    return redirect(url_for("profile.show_profile"))

@profile.get("/profile/demos")
@login_required
def list_demos():
    demos = (Demo.query
             .filter_by(user_id=current_user.id)
             .order_by(Demo.updated_at.desc())
             .all())

    items = []
    for d in demos:
        try:
            url = presigned_get_url(d.key, expires_in=3600)
        except Exception:
            url = None
        items.append({"id": d.id, "title": d.title, "mime": d.mime, "url": url, "updated_at": d.updated_at})

    return render_template("partials/_demos_list.html", items=items)

###Skills###

@profile.post("/profile/skills/add")
@login_required
def add_skill():
    name = request.form.get("instrument", "").strip()
    level = request.form.get("level")
    years = request.form.get("years", 0, type=int)

    if not name or not level:
        flash("Skill name and level are required.", "danger")
        return redirect(url_for("profile.show_profile"))

    # Get or create the Skill catalog entry
    skill = Skill.query.filter_by(name=name).first()
    if not skill:
        skill = Skill(name=name)
        db.session.add(skill)
        db.session.flush()  # so it gets an id

    # Attach to user
    user_skill = UserSkill(user_id=current_user.id, skill=skill, level=level, years=years)
    db.session.add(user_skill)
    db.session.commit()

    flash(f"Added skill {name} ({level}, {years} yrs).", "success")
    return redirect(url_for("profile.show_profile"))


@profile.post("/profile/skills/delete/<int:user_skill_id>")
@login_required
def delete_skill(user_skill_id):
    us = UserSkill.query.filter_by(id=user_skill_id, user_id=current_user.id).first_or_404()
    db.session.delete(us)
    db.session.commit()
    flash("Skill removed.", "success")
    return redirect(url_for("profile.show_profile"))
