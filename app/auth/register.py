from flask import render_template, redirect, url_for, request, flash
from .models import User
from app.extensions import db

def handle_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return render_template('register.html')

        user = User(username = username, email = email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('google.login'))

    return render_template('register.html')
