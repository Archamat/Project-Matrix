from app.extensions import db
from app.auth.models import User
from app.projects.models import Project
from app.profile.models import Skill
from sqlalchemy import func


class SearchDatabaseManager:
    """Handles all search-related database operations"""

    @staticmethod
    def _search_users(query, limit=None, offset=0):
        """
        Search for users by username or bio
        
        Args:sss
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of users, total count)
        """
        if not query:
            return [], 0
            
        like = f"%{query}%"
        base_query = User.query.filter(
            (User.username.ilike(like)) | (func.coalesce(User.bio, "").ilike(like))
        )
        
        total_count = base_query.count()
        users_query = base_query.order_by(User.username.asc())
        
        if limit:
            users_query = users_query.limit(limit).offset(offset)
        
        return users_query.all(), total_count

    @staticmethod
    def _search_projects(query, limit=None, offset=0):
        """
        Search for projects by name or description
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of projects, total count)
        """
        if not query:
            return [], 0
            
        like = f"%{query}%"
        base_query = Project.query.filter(
            (Project.name.ilike(like)) | (func.coalesce(Project.description, "").ilike(like))
        )
        
        total_count = base_query.count()
        projects_query = base_query.order_by(Project.name.asc())
        
        if limit:
            projects_query = projects_query.limit(limit).offset(offset)
        
        return projects_query.all(), total_count

    @staticmethod
    def _search_skills(query, limit=None, offset=0):
        """
        Search for skills by name
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of skills, total count)
        """
        if not query:
            return [], 0
            
        like = f"%{query}%"
        base_query = Skill.query.filter(Skill.name.ilike(like))
        
        total_count = base_query.count()
        skills_query = base_query.order_by(Skill.name.asc())
        
        if limit:
            skills_query = skills_query.limit(limit).offset(offset)
        
        return skills_query.all(), total_count

    @staticmethod
    def search_all(query, preview_limit=5):
        """
        Search across all entities (users, projects, skills)
        
        Args:
            query: Search query string
            preview_limit: Number of preview results per category
            
        Returns:
            dict: Results for each category with counts
        """
        if not query:
            return {
                "users": [],
                "projects": [],
                "skills": [],
                "counts": {"users": 0, "projects": 0, "skills": 0}
            }
        users_preview, users_count = SearchDatabaseManager._search_users(query, limit=preview_limit)
        projects_preview, projects_count = SearchDatabaseManager._search_projects(query, limit=preview_limit)
        skills_preview, skills_count = SearchDatabaseManager._search_skills(query, limit=preview_limit)
        
        return {
            "users": users_preview,
            "projects": projects_preview,
            "skills": skills_preview,
            "counts": {
                "users": users_count,
                "projects": projects_count,
                "skills": skills_count
            }
        }

