from flask import Blueprint, request, jsonify
from .search_database_manager import SearchDatabaseManager
from app.auth.models import User
from app.projects.models import Project
from app.profile.models import Skill

search_api = Blueprint('search_api', __name__, url_prefix='/api/search')


def serialize_user(user):
    """Serialize user to dictionary"""
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'bio': user.bio or '',
        'contact_info': user.contact_info or '',
        'avatar_url': user.avatar_presigned if hasattr(user, 'avatar_presigned') else None
    }


def serialize_project(project):
    """Serialize project to dictionary"""
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'sector': project.sector,
        'people_count': project.people_count,
        'skills': project.skills.split(',') if project.skills else [],
        'creator_id': project.creator_id
    }


def serialize_skill(skill):
    """Serialize skill to dictionary"""
    return {
        'id': skill.id,
        'name': skill.name
    }


@search_api.route('/all', methods=['GET'])
def search_all():
    """Search across all entities (users, projects, skills)"""
    try:
        query = (request.args.get('q') or '').strip()
        preview_limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({
                'success': True,
                'query': '',
                'users': [],
                'projects': [],
                'skills': [],
                'counts': {'users': 0, 'projects': 0, 'skills': 0},
                'message': 'Type something to search.'
            }), 200
        
        results = SearchDatabaseManager.search_all(query, preview_limit=preview_limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'users': [serialize_user(u) for u in results['users']],
            'projects': [serialize_project(p) for p in results['projects']],
            'skills': [serialize_skill(s) for s in results['skills']],
            'counts': results['counts']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@search_api.route('/users', methods=['GET'])
def search_users():
    """Search for users only"""
    try:
        query = (request.args.get('q') or '').strip()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        users, total_count = SearchDatabaseManager.search_users(query, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'query': query,
            'users': [serialize_user(u) for u in users],
            'count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@search_api.route('/projects', methods=['GET'])
def search_projects():
    """Search for projects only"""
    try:
        query = (request.args.get('q') or '').strip()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        projects, total_count = SearchDatabaseManager.search_projects(query, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'query': query,
            'projects': [serialize_project(p) for p in projects],
            'count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@search_api.route('/skills', methods=['GET'])
def search_skills():
    """Search for skills only"""
    try:
        query = (request.args.get('q') or '').strip()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        skills, total_count = SearchDatabaseManager.search_skills(query, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'query': query,
            'skills': [serialize_skill(s) for s in skills],
            'count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

