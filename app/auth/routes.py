from flask import Blueprint, render_template
from .login import handle_login
from .register import handle_register
from .logout import handle_logout

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic here...
    return handle_login()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Registration logic here...
    return handle_register()

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    # Login logic here...
    return handle_logout()


