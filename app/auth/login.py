from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user
from .models import User

# Login route logic
def handle_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Login failed, please check your username and password')

    return render_template('login.html' , current_page='google.login')
