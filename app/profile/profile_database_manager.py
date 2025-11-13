from app.extensions import db
from app.auth.models import User
from app.profile.models import Demo, Skill, UserSkill
from app.aws.s3 import s3_client, S3_BUCKET
from sqlalchemy.exc import IntegrityError


class ProfileDatabaseManager:
    """Handles all profile-related database operations"""

    @staticmethod
    def get_user_by_username(username):
        """Fetch user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def update_user_profile(user, data):
        """Update user profile fields"""
        try:
            # Check if username is taken by another user
            if 'username' in data and data['username'] != user.username:
                existing = User.query.filter_by(
                    username=data['username']).first()
                if existing:
                    raise ValueError('Username already exists')

            # Check if email is taken by another user
            if 'email' in data and data['email'] != user.email:
                existing = User.query.filter_by(email=data['email']).first()
                if existing:
                    raise ValueError('Email already exists')

            # Update fields
            for field in ['username', 'email',
                          'contact_info', 'bio', 'avatar_url']:
                if field in data:
                    setattr(user, field, data[field])

            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Database integrity error')
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_avatar(user, s3_key):
        """Update user's avatar URL"""
        try:
            user.avatar_url = s3_key
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    # ==================== DEMOS ====================
    @staticmethod
    def create_demo(user_id, s3_key, title, mime_type):
        """Create a new demo entry"""
        try:
            demo = Demo(
                user_id=user_id,
                key=s3_key,
                title=title,
                mime=mime_type
            )
            db.session.add(demo)
            db.session.commit()
            return demo
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_demos(user_id, limit=None):
        """Get all demos for a user"""
        query = Demo.query.filter_by(user_id=user_id).order_by(
            Demo.updated_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_demo_by_id(demo_id, user_id):
        """Get a specific demo owned by user"""
        return Demo.query.filter_by(id=demo_id, user_id=user_id).first()

    @staticmethod
    def delete_demo(demo):
        """Delete demo from DB and S3"""
        try:
            # Delete from S3
            s3_client.delete_object(Bucket=S3_BUCKET, Key=demo.key)
            # Delete from DB
            db.session.delete(demo)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # ==================== SKILLS ====================
    @staticmethod
    def get_or_create_skill(skill_name):
        """Get existing skill or create new one"""
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            skill = Skill(name=skill_name)
            db.session.add(skill)
            db.session.flush()  # Get ID without committing
        return skill

    @staticmethod
    def add_user_skill(user_id, skill_name, level, years):
        """Add a skill to user's profile"""
        try:
            skill = ProfileDatabaseManager.get_or_create_skill(skill_name)

            # Check if user already has this skill
            existing = UserSkill.query.filter_by(
                user_id=user_id,
                skill_id=skill.id
            ).first()

            if existing:
                raise ValueError
            (f'You already have {skill_name} in your skills')

            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill.id,
                level=level,
                years=years
            )
            db.session.add(user_skill)
            db.session.commit()
            return user_skill
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Skill already exists')
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_skill(user_skill_id, user_id):
        """Get a specific user skill"""
        return UserSkill.query.filter_by(id=user_skill_id,
                                         user_id=user_id).first()

    @staticmethod
    def delete_user_skill(user_skill):
        """Remove a skill from user's profile"""
        try:
            db.session.delete(user_skill)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
