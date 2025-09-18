from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user,login_required
from app import db
from app.auth import User
from app.aws.s3 import presigned_get_url
from app.profile.models import Demo

def handle_profile(username: str | None = None):
    """
    Render a profile. If username is None, show the current user's profile.
    Used by:
      - /profile                -> handle_profile()
      - /u/<username> (public)  -> handle_profile(username)
    """
    #pick a target user
    if username and username != current_user.username:
        user = User.query.filter_by(username=username).first_or_404()
        is_owner = False
    else:
        user = current_user
        is_owner = True 
    demos = []
    for d in (Demo.query.filter_by(user_id=user.id).order_by(Demo.updated_at.desc()).all()):
        url = presigned_get_url(d.key, 3600)
        demos.append({
            "id": d.id,
            "title": d.title or "Untitled",
            "mime": d.mime,
            "url": url,
            "visibility": d.visibility or "Private",
            "updated_at": d.updated_at,
        })
    return render_template('profile.html', user=user, demos=demos, is_owner=is_owner, current_page='profile')

@login_required
def update_profile():
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            contact_info = request.form.get('contact_info')
            avatar_url = request.form.get('avatar_url')
            # Validate required fields
            if not username or not email:
                flash('Username and email are required.', 'error')
                return redirect(url_for('profile.show_profile'))
            
            # Check if username is already taken by another user
            existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
                return redirect(url_for('profile.show_profile'))
            
            # Check if email is already taken by another user
            existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_email:
                flash('Email already exists. Please choose a different one.', 'error')
                return redirect(url_for('profile.show_profile'))
            
            # Update user information
            current_user.username = username
            current_user.email = email
            current_user.contact_info = contact_info
            current_user.avatar_url = request.form.get("avatar_url").strip()
            current_user.bio = (request.form.get("bio") or "").strip()
            # Commit changes to database
            db.session.commit()
            
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'error')
            
        return redirect(url_for('profile.show_profile'))

    return redirect(url_for('profile.show_profile'))