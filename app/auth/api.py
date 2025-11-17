from flask import Blueprint
from .auth import handle_login, handle_register, handle_logout
from flask import request, jsonify

auth_api = Blueprint('auth_api', __name__)


@auth_api.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        handle_login(data)
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


@auth_api.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        handle_register(data)
        return jsonify({'success': True, 'message': ''
                        'Registration successful'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


@auth_api.route('/api/logout', methods=['POST'])
def logout():
    try:
        handle_logout()
        return jsonify({'success': True, 'message': 'Logout successful'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500
