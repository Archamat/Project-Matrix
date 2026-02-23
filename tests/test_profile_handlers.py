"""
Tests for profile business logic handlers
"""

import pytest
from app.profile.profile import (
    handle_profile,
    handle_update_profile,
    handle_avatar_upload,
    handle_skill_add,
    handle_skill_delete,
)
from app.profile.models import UserSkill


class TestHandleProfile:
    """Tests for handle_profile function"""

    def test_handle_profile_returns_user(self, app, test_user):
        """Test that handle_profile returns user data"""
        with app.app_context():
            result = handle_profile(test_user)

            assert "user" in result
            assert result["user"].id == test_user.id
            assert result["user"].username == test_user.username

    def test_handle_profile_returns_participated_projects(
        self, app, test_user
    ):
        """Test that handle_profile includes participated projects"""
        with app.app_context():
            result = handle_profile(test_user)

            assert "participated_projects" in result
            assert isinstance(result["participated_projects"], list)

    def test_handle_profile_empty_projects(self, app, test_user):
        """Test handle_profile with user who has no projects"""
        with app.app_context():
            result = handle_profile(test_user)

            assert len(result["participated_projects"]) == 0


class TestHandleUpdateProfile:
    """Tests for handle_update_profile function"""

    def test_update_profile_success(self, app, test_user):
        """Test successful profile update"""
        with app.app_context():
            data = {
                "username": "newuser",
                "email": "newemail@example.com",
                "bio": "New bio",
                "contact_info": "New contact",
            }
            updated_user = handle_update_profile(test_user, data)

            assert updated_user.username == "newuser"
            assert updated_user.email == "newemail@example.com"
            assert updated_user.bio == "New bio"
            assert updated_user.contact_info == "New contact"

    def test_update_profile_missing_username(self, app, test_user):
        """Test that username is required"""
        with app.app_context():
            data = {"email": "test@example.com"}
            with pytest.raises(
                ValueError, match="Username and email are required"
            ):
                handle_update_profile(test_user, data)

    def test_update_profile_missing_email(self, app, test_user):
        """Test that email is required"""
        with app.app_context():
            data = {"username": "testuser"}
            with pytest.raises(
                ValueError, match="Username and email are required"
            ):
                handle_update_profile(test_user, data)

    def test_update_profile_strips_whitespace(self, app, test_user):
        """Test that input is sanitized (whitespace stripped)"""
        with app.app_context():
            data = {
                "username": "  newuser  ",
                "email": "  newemail@example.com  ",
                "bio": "  New bio  ",
                "contact_info": "  New contact  ",
            }
            updated_user = handle_update_profile(test_user, data)

            assert updated_user.username == "newuser"
            assert updated_user.email == "newemail@example.com"
            assert updated_user.bio == "New bio"
            assert updated_user.contact_info == "New contact"

    def test_update_profile_duplicate_username(
        self, app, test_user, test_user2
    ):
        """Test that duplicate username raises error"""
        with app.app_context():
            data = {"username": "testuser2", "email": "test@example.com"}
            with pytest.raises(ValueError, match="Username already exists"):
                handle_update_profile(test_user, data)

    def test_update_profile_duplicate_email(self, app, test_user, test_user2):
        """Test that duplicate email raises error"""
        with app.app_context():
            data = {"username": "testuser", "email": "test2@example.com"}
            with pytest.raises(ValueError, match="Email already exists"):
                handle_update_profile(test_user, data)


class TestHandleAvatarUpload:
    """Tests for handle_avatar_upload function"""

    def test_avatar_upload_success(self, app, test_user):
        """Test successful avatar upload"""
        with app.app_context():
            s3_key = "avatars/123/avatar.jpg"
            updated_user = handle_avatar_upload(test_user, s3_key)

            assert updated_user.avatar_url == s3_key

    def test_avatar_upload_missing_key(self, app, test_user):
        """Test that missing S3 key raises error"""
        with app.app_context():
            with pytest.raises(ValueError, match="S3 key is required"):
                handle_avatar_upload(test_user, None)

    def test_avatar_upload_empty_key(self, app, test_user):
        """Test that empty S3 key raises error"""
        with app.app_context():
            with pytest.raises(ValueError, match="S3 key is required"):
                handle_avatar_upload(test_user, "")


class TestHandleSkillAdd:
    """Tests for handle_skill_add function"""

    def test_add_skill_success(self, app, test_user):
        """Test successfully adding a skill"""
        with app.app_context():
            user_skill = handle_skill_add(
                test_user, "Python", "Intermediate", 3
            )

            assert user_skill.id is not None
            assert user_skill.skill.name == "Python"
            assert user_skill.level == "Intermediate"
            assert user_skill.years == 3

    def test_add_skill_missing_name(self, app, test_user):
        """Test that skill name is required"""
        with app.app_context():
            with pytest.raises(
                ValueError, match="Skill name and level are required"
            ):
                handle_skill_add(test_user, "", "Intermediate", 3)

    def test_add_skill_missing_level(self, app, test_user):
        """Test that level is required"""
        with app.app_context():
            with pytest.raises(
                ValueError, match="Skill name and level are required"
            ):
                handle_skill_add(test_user, "Python", None, 3)

    def test_add_skill_invalid_level(self, app, test_user):
        """Test that invalid level raises error"""
        with app.app_context():
            with pytest.raises(ValueError, match="Level must be one of"):
                handle_skill_add(test_user, "Python", "Invalid", 3)

    def test_add_skill_valid_levels(self, app, test_user):
        """Test all valid skill levels"""
        valid_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
        with app.app_context():
            for level in valid_levels:
                user_skill = handle_skill_add(
                    test_user, f"Skill{level}", level, 1
                )
                assert user_skill.level == level

    def test_add_skill_invalid_years_negative(self, app, test_user):
        """Test that negative years raises error"""
        with app.app_context():
            with pytest.raises(
                ValueError, match="Years must be between 0 and 50"
            ):
                handle_skill_add(test_user, "Python", "Intermediate", -1)

    def test_add_skill_invalid_years_too_high(self, app, test_user):
        """Test that years > 50 raises error"""
        with app.app_context():
            with pytest.raises(
                ValueError, match="Years must be between 0 and 50"
            ):
                handle_skill_add(test_user, "Python", "Intermediate", 51)

    def test_add_skill_valid_years_boundary(self, app, test_user):
        """Test valid years boundaries"""
        with app.app_context():
            # Test 0 years
            user_skill1 = handle_skill_add(test_user, "Skill0", "Beginner", 0)
            assert user_skill1.years == 0

            # Test 50 years
            user_skill2 = handle_skill_add(test_user, "Skill50", "Expert", 50)
            assert user_skill2.years == 50

    def test_add_skill_invalid_years_type(self, app, test_user):
        """Test that non-numeric years raises error"""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid years value"):
                handle_skill_add(
                    test_user, "Python", "Intermediate", "not-a-number"
                )

    def test_add_skill_duplicate(self, app, test_user):
        """Test that adding duplicate skill raises error"""
        with app.app_context():
            handle_skill_add(test_user, "Python", "Beginner", 1)

            with pytest.raises(ValueError):
                handle_skill_add(test_user, "Python", "Intermediate", 2)


class TestHandleSkillDelete:
    """Tests for handle_skill_delete function"""

    def test_delete_skill_success(self, app, test_user, test_skill):
        """Test successfully deleting a skill"""
        with app.app_context():
            user_skill = handle_skill_add(
                test_user, "Python", "Intermediate", 3
            )
            skill_id = user_skill.id

            result = handle_skill_delete(test_user, skill_id)

            assert result is True
            deleted = UserSkill.query.filter_by(id=skill_id).first()
            assert deleted is None

    def test_delete_nonexistent_skill(self, app, test_user):
        """Test deleting a skill that doesn't exist"""
        with app.app_context():
            with pytest.raises(
                ValueError, match="Skill not found or unauthorized"
            ):
                handle_skill_delete(test_user, 999)

    def test_delete_other_user_skill(
        self, app, test_user, test_user2, test_skill
    ):
        """Test that user cannot delete another user's skill"""
        with app.app_context():
            # Add skill to test_user2
            user_skill = handle_skill_add(
                test_user2, "Python", "Intermediate", 3
            )
            skill_id = user_skill.id

            # Try to delete from test_user
            with pytest.raises(
                ValueError, match="Skill not found or unauthorized"
            ):
                handle_skill_delete(test_user, skill_id)
