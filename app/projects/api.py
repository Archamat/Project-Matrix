from flask import Blueprint
from .project import (handle_project_create, handle_apply_project,
                      get_project_applicants, get_project_by_id,
                      get_all_projects)
from flask import request, jsonify
from flask_login import current_user, login_required

project_api = Blueprint('project_api', __name__)


@project_api.route('/api/projects', methods=['GET'])
def get_projects():
    projects = get_all_projects()
    return jsonify({
        'projects': [p.to_dict() for p in projects]
    }), 200


@project_api.route('/api/project/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = get_project_by_id(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify(project.to_dict()), 200


@project_api.route('/api/create_project', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        handle_project_create(
            name=data['name'],
            description=data['description'],
            sector=data['sector'],
            people_count=data['people_count'],
            skills=data.get('skills', []),
            other_skill=data.get('other_skill'),
            creator_id=current_user.id
        )
        return jsonify({'success': True, 'message': 'Project created '
                        'successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


@project_api.route('/api/apply/<int:project_id>', methods=['POST'])
def apply_project(project_id):
    form = request.get_json()
    try:
        handle_apply_project(project_id, form, current_user.id)
        return jsonify({'success': True, 'message': 'Application '
                        'submitted successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


@project_api.route('/api/project/<int:project_id>/applicants', methods=['GET'])
@login_required
def project_applicants(project_id):
    """Get all applicants for a project."""
    try:
        applicants = get_project_applicants(project_id, current_user.id)

        return jsonify({
            'applicants': [app.to_dict() for app in applicants]
        }), 200

    except ValueError as e:
        # Project not found
        return jsonify({'error': str(e)}), 404

    except PermissionError as e:
        # User not authorized
        return jsonify({'error': str(e)}), 403

    except Exception:
        # Unexpected error
        return jsonify({'error': 'Internal server error'}), 500
