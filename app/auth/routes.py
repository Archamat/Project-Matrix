from flask_dance.contrib.google import make_google_blueprint, google
from flask import Flask, redirect, url_for, flash
from flask_login import login_user, current_user
from .models import User, db

blueprint = make_google_blueprint(
    client_id="your-client-id",
    client_secret="your-client-secret",
    scope=["profile", "email"]
)

@blueprint.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    
    google_info = resp.json()
    google_user_id = google_info["id"]
    
    user = User.query.filter_by(google_id=google_user_id).first()
    if not user:
        # Create user
        user = User(
            username=google_info["email"].split('@')[0],
            email=google_info["email"],
            google_id=google_user_id
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    flash('Logged in successfully.')
    return redirect(url_for('main.home'))