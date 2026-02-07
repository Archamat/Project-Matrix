"""
Tests for profile models: Skill and UserSkill
"""

import pytest
from app.profile.models import Skill, UserSkill
from app.extensions import db
from sqlalchemy.exc import IntegrityError


class TestSkillModel:
    """Tests for the Skill model"""

    def test_create_skill(self, app):
        """Test creating a skill"""
        with app.app_context():
            skill = Skill(name="Python")
            db.session.add(skill)
            db.session.commit()

            assert skill.id is not None
            assert skill.name == "Python"
            assert len(skill.user_skills) == 0

    def test_skill_unique_name(self, app):
        """Test that skill names must be unique"""
        with app.app_context():
            skill1 = Skill(name="Python")
            db.session.add(skill1)
            db.session.commit()

            skill2 = Skill(name="Python")
            db.session.add(skill2)

            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_skill_relationship_with_user_skills(self, app, test_user):
        """Test relationship between Skill and UserSkill"""
        with app.app_context():
            skill = Skill(name="JavaScript")
            db.session.add(skill)
            db.session.flush()

            user_skill = UserSkill(
                user_id=test_user.id,
                skill_id=skill.id,
                level="Expert",
                years=5,
            )
            db.session.add(user_skill)
            db.session.commit()

            assert len(skill.user_skills) == 1
            assert skill.user_skills[0].user_id == test_user.id


class TestUserSkillModel:
    """Tests for the UserSkill model"""

    def test_create_user_skill(self, app, test_user, test_skill):
        """Test creating a user skill"""
        with app.app_context():
            user_skill = UserSkill(
                user_id=test_user.id,
                skill_id=test_skill.id,
                level="Beginner",
                years=1,
            )
            db.session.add(user_skill)
            db.session.commit()

            assert user_skill.id is not None
            assert user_skill.user_id == test_user.id
            assert user_skill.skill_id == test_skill.id
            assert user_skill.level == "Beginner"
            assert user_skill.years == 1

    def test_user_skill_unique_constraint(self, app, test_user, test_skill):
        """Test that a user cannot have the same skill twice"""
        with app.app_context():
            user_skill1 = UserSkill(
                user_id=test_user.id,
                skill_id=test_skill.id,
                level="Beginner",
                years=1,
            )
            db.session.add(user_skill1)
            db.session.commit()

            user_skill2 = UserSkill(
                user_id=test_user.id,
                skill_id=test_skill.id,
                level="Intermediate",
                years=2,
            )
            db.session.add(user_skill2)

            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_user_skill_relationship_with_user(
        self, app, test_user, test_skill
    ):
        """Test relationship between UserSkill and User"""
        with app.app_context():
            user_skill = UserSkill(
                user_id=test_user.id,
                skill_id=test_skill.id,
                level="Advanced",
                years=4,
            )
            db.session.add(user_skill)
            db.session.commit()

            assert user_skill.user.id == test_user.id
            assert user_skill.user.username == test_user.username

    def test_user_skill_relationship_with_skill(
        self, app, test_user, test_skill
    ):
        """Test relationship between UserSkill and Skill"""
        with app.app_context():
            user_skill = UserSkill(
                user_id=test_user.id,
                skill_id=test_skill.id,
                level="Expert",
                years=6,
            )
            db.session.add(user_skill)
            db.session.commit()

            assert user_skill.skill.id == test_skill.id
            assert user_skill.skill.name == test_skill.name

    def test_user_skill_optional_fields(self, app, test_user, test_skill):
        """Test that level and years are optional"""
        with app.app_context():
            user_skill = UserSkill(
                user_id=test_user.id, skill_id=test_skill.id
            )
            db.session.add(user_skill)
            db.session.commit()

            assert user_skill.level is None
            assert user_skill.years is None
