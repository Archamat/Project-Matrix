"""
Tests for ProfileDatabaseManager - database operations
"""

import pytest
from app.profile.profile_database_manager import ProfileDatabaseManager
from app.profile.models import Skill, UserSkill
from app.extensions import db


class TestProfileDatabaseManager:
    """Tests for ProfileDatabaseManager class"""

    class TestGetUserByUsername:
        """Tests for get_user_by_username method"""

        def test_get_existing_user(self, app, test_user):
            """Test getting an existing user by username"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                assert user is not None
                assert user.username == "testuser"
                assert user.email == "test@example.com"

        def test_get_nonexistent_user(self, app):
            """Test getting a user that doesn't exist"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username(
                    "nonexistent"
                )
                assert user is None

    class TestUpdateUserProfile:
        """Tests for update_user_profile method"""

        def test_update_profile_success(self, app, test_user):
            """Test successful profile update"""
            with app.app_context():
                # Get fresh user from this session
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                data = {
                    "username": "newusername",
                    "email": "newemail@example.com",
                    "bio": "New bio",
                    "contact_info": "New contact",
                }
                updated_user = ProfileDatabaseManager.update_user_profile(
                    user, data
                )

                assert updated_user.username == "newusername"
                assert updated_user.email == "newemail@example.com"
                assert updated_user.bio == "New bio"
                assert updated_user.contact_info == "New contact"

        def test_update_profile_partial(self, app, test_user):
            """Test updating only some fields"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                original_email = user.email
                data = {"bio": "Updated bio only"}
                updated_user = ProfileDatabaseManager.update_user_profile(
                    user, data
                )

                assert updated_user.bio == "Updated bio only"
                assert updated_user.email == original_email

        def test_update_username_duplicate(self, app, test_user, test_user2):
            """Test updating username to one that already exists"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                data = {"username": "testuser2"}
                with pytest.raises(
                    ValueError, match="Username already exists"
                ):
                    ProfileDatabaseManager.update_user_profile(user, data)

        def test_update_email_duplicate(self, app, test_user, test_user2):
            """Test updating email to one that already exists"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                data = {"email": "test2@example.com"}
                with pytest.raises(ValueError, match="Email already exists"):
                    ProfileDatabaseManager.update_user_profile(user, data)

        def test_update_same_username_allowed(self, app, test_user):
            """Test that updating to the same username is allowed"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                data = {"username": "testuser", "bio": "New bio"}
                updated_user = ProfileDatabaseManager.update_user_profile(
                    user, data
                )
                assert updated_user.username == "testuser"
                assert updated_user.bio == "New bio"

        def test_update_same_email_allowed(self, app, test_user):
            """Test that updating to the same email is allowed"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                data = {"email": "test@example.com", "bio": "New bio"}
                updated_user = ProfileDatabaseManager.update_user_profile(
                    user, data
                )
                assert updated_user.email == "test@example.com"
                assert updated_user.bio == "New bio"

    class TestUpdateAvatar:
        """Tests for update_avatar method"""

        def test_update_avatar_success(self, app, test_user):
            """Test successful avatar update"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                s3_key = "avatars/123/avatar.jpg"
                updated_user = ProfileDatabaseManager.update_avatar(
                    user, s3_key
                )

                assert updated_user.avatar_url == s3_key

        def test_update_avatar_overwrite(self, app, test_user):
            """Test overwriting existing avatar"""
            with app.app_context():
                user = ProfileDatabaseManager.get_user_by_username("testuser")
                user.avatar_url = "avatars/123/old.jpg"
                db.session.commit()

                new_key = "avatars/123/new.jpg"
                updated_user = ProfileDatabaseManager.update_avatar(
                    user, new_key
                )

                assert updated_user.avatar_url == new_key

    class TestGetOrCreateSkill:
        """Tests for get_or_create_skill method"""

        def test_get_existing_skill(self, app, test_skill):
            """Test getting an existing skill"""
            with app.app_context():
                skill = ProfileDatabaseManager.get_or_create_skill("Python")
                assert skill.name == "Python"

        def test_create_new_skill(self, app):
            """Test creating a new skill"""
            with app.app_context():
                skill = ProfileDatabaseManager.get_or_create_skill(
                    "JavaScript"
                )
                assert skill.id is not None
                assert skill.name == "JavaScript"

                # Verify it was saved
                db.session.commit()
                saved_skill = Skill.query.filter_by(name="JavaScript").first()
                assert saved_skill is not None

    class TestAddUserSkill:
        """Tests for add_user_skill method"""

        def test_add_user_skill_success(self, app, test_user):
            """Test successfully adding a skill to user"""
            with app.app_context():
                user_skill = ProfileDatabaseManager.add_user_skill(
                    test_user.id, "Python", "Intermediate", 3
                )

                assert user_skill.id is not None
                assert user_skill.user_id == test_user.id
                assert user_skill.level == "Intermediate"
                assert user_skill.years == 3
                assert user_skill.skill.name == "Python"

        def test_add_user_skill_creates_skill(self, app, test_user):
            """Test that adding a skill creates the skill if it doesn't exist"""
            with app.app_context():
                user_skill = ProfileDatabaseManager.add_user_skill(
                    test_user.id, "NewSkill", "Beginner", 1
                )

                assert user_skill.skill.name == "NewSkill"
                skill = Skill.query.filter_by(name="NewSkill").first()
                assert skill is not None

        def test_add_duplicate_skill(self, app, test_user, test_skill):
            """Test that adding duplicate skill raises error"""
            with app.app_context():
                # Add skill first time
                ProfileDatabaseManager.add_user_skill(
                    test_user.id, "Python", "Beginner", 1
                )

                # Try to add again
                with pytest.raises(ValueError):
                    ProfileDatabaseManager.add_user_skill(
                        test_user.id, "Python", "Intermediate", 2
                    )

        def test_add_skill_different_users(self, app, test_user, test_user2):
            """Test that different users can have the same skill"""
            with app.app_context():
                user_skill1 = ProfileDatabaseManager.add_user_skill(
                    test_user.id, "Python", "Beginner", 1
                )
                user_skill2 = ProfileDatabaseManager.add_user_skill(
                    test_user2.id, "Python", "Expert", 5
                )

                assert user_skill1.user_id == test_user.id
                assert user_skill2.user_id == test_user2.id
                assert user_skill1.skill_id == user_skill2.skill_id

    class TestGetUserSkill:
        """Tests for get_user_skill method"""

        def test_get_existing_user_skill(self, app, test_user, test_skill):
            """Test getting an existing user skill"""
            with app.app_context():
                # Create the user skill within this context
                user_skill = UserSkill(
                    user_id=test_user.id,
                    skill_id=test_skill.id,
                    level="Intermediate",
                    years=3,
                )
                db.session.add(user_skill)
                db.session.commit()
                skill_id = user_skill.id

                fetched = ProfileDatabaseManager.get_user_skill(
                    skill_id, test_user.id
                )

                assert fetched is not None
                assert fetched.id == skill_id

        def test_get_nonexistent_user_skill(self, app, test_user):
            """Test getting a skill that doesn't exist"""
            with app.app_context():
                user_skill = ProfileDatabaseManager.get_user_skill(
                    999, test_user.id
                )
                assert user_skill is None

        def test_get_user_skill_wrong_user(
            self, app, test_user, test_user2, test_skill
        ):
            """Test that user cannot get another user's skill"""
            with app.app_context():
                # Create skill for test_user
                user_skill = UserSkill(
                    user_id=test_user.id,
                    skill_id=test_skill.id,
                    level="Intermediate",
                    years=3,
                )
                db.session.add(user_skill)
                db.session.commit()
                skill_id = user_skill.id

                # Try to get it as test_user2
                fetched = ProfileDatabaseManager.get_user_skill(
                    skill_id, test_user2.id
                )
                assert fetched is None

    class TestDeleteUserSkill:
        """Tests for delete_user_skill method"""

        def test_delete_user_skill_success(self, app, test_user, test_skill):
            """Test successfully deleting a user skill"""
            with app.app_context():
                # Create the user skill within this context
                user_skill = UserSkill(
                    user_id=test_user.id,
                    skill_id=test_skill.id,
                    level="Intermediate",
                    years=3,
                )
                db.session.add(user_skill)
                db.session.commit()
                skill_id = user_skill.id

                ProfileDatabaseManager.delete_user_skill(user_skill)

                deleted = UserSkill.query.filter_by(id=skill_id).first()
                assert deleted is None

        def test_delete_user_skill_preserves_skill(
            self, app, test_user, test_skill
        ):
            """Test that deleting user skill doesn't delete the skill itself"""
            with app.app_context():
                # Get fresh skill reference
                skill = Skill.query.filter_by(name="Python").first()
                skill_id = skill.id

                # Create the user skill within this context
                user_skill = UserSkill(
                    user_id=test_user.id,
                    skill_id=skill_id,
                    level="Intermediate",
                    years=3,
                )
                db.session.add(user_skill)
                db.session.commit()

                ProfileDatabaseManager.delete_user_skill(user_skill)

                # Skill should still exist
                preserved_skill = Skill.query.filter_by(id=skill_id).first()
                assert preserved_skill is not None
