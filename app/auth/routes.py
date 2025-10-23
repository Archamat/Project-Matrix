from flask import Blueprint, render_template
from .auth import handle_login, handle_register, handle_logout
from flask import request, jsonify

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic here...
    if request.method == 'GET':
        return render_template('login.html')
    data = request.get_json()
    result = handle_login(data)
    return jsonify(result)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Registration logic here...
    if request.method == 'GET':
        return render_template('register.html')
    data = request.get_json()
    result = handle_register(data)
    return jsonify(result)


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    result = handle_logout()
    return jsonify(result)
