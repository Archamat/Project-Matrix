"""
Tests for profile view routes
"""

from unittest.mock import patch
from io import BytesIO
import importlib
from app.profile.models import UserSkill


class TestShowProfile:
    """Tests for /profile endpoint"""

    def test_show_profile_requires_login(self, client):
        """Test that profile page requires authentication"""
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 302

    def test_show_profile_authenticated(self, authenticated_client, test_user):
        """Test authenticated user can view profile"""
        response = authenticated_client.get("/profile")
        assert response.status_code == 200

    def test_show_profile_owner_flag(self, authenticated_client, test_user):
        """Test that is_owner is True for own profile"""
        response = authenticated_client.get("/profile")
        assert response.status_code == 200
        assert b"testuser" in response.data


class TestViewProfile:
    """Tests for /u/<username> endpoint"""

    def test_view_other_user_profile(
        self, authenticated_client, test_user, test_user2
    ):
        """Test viewing another user's profile"""
        response = authenticated_client.get(f"/u/{test_user2.username}")
        assert response.status_code == 200

    def test_view_nonexistent_user(self, authenticated_client, test_user):
        """Test viewing nonexistent user returns 404"""
        response = authenticated_client.get("/u/nonexistentuser")
        assert response.status_code == 404

    def test_view_own_profile_via_username(
        self, authenticated_client, test_user
    ):
        """Test viewing own profile via username URL"""
        response = authenticated_client.get(f"/u/{test_user.username}")
        assert response.status_code == 200


class TestUploadAvatar:
    """Tests for /profile/avatar endpoint"""

    def test_upload_avatar_success(self, authenticated_client, test_user, app):
        """Test successful avatar upload"""
        routes_module = importlib.import_module("app.profile.routes")
        with patch.object(
            routes_module, "upload_fileobj_private"
        ) as mock_upload:
            mock_upload.return_value = {"key": "avatars/1/test.jpg"}

            data = {
                "avatar_file": (
                    BytesIO(b"fake image data"),
                    "test.jpg",
                    "image/jpeg",
                )
            }
            response = authenticated_client.post(
                "/profile/avatar",
                data=data,
                content_type="multipart/form-data",
                follow_redirects=False,
            )

            assert response.status_code == 302  # Redirect after success

    def test_upload_avatar_no_file(self, authenticated_client):
        """Test avatar upload without file"""
        response = authenticated_client.post(
            "/profile/avatar",
            data={},
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        assert response.status_code == 302  # Redirect with flash message

    def test_upload_avatar_invalid_mimetype(self, authenticated_client):
        """Test avatar upload with invalid file type"""
        data = {
            "avatar_file": (
                BytesIO(b"fake pdf data"),
                "test.pdf",
                "application/pdf",
            )
        }
        response = authenticated_client.post(
            "/profile/avatar",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        assert response.status_code == 302  # Redirect with flash message

    def test_upload_avatar_upload_failure(self, authenticated_client, app):
        """Test avatar upload when upload fails"""
        routes_module = importlib.import_module("app.profile.routes")
        with patch.object(
            routes_module, "upload_fileobj_private"
        ) as mock_upload:
            mock_upload.side_effect = Exception("Upload failed")

            data = {
                "avatar_file": (
                    BytesIO(b"fake image data"),
                    "test.jpg",
                    "image/jpeg",
                )
            }
            response = authenticated_client.post(
                "/profile/avatar",
                data=data,
                content_type="multipart/form-data",
                follow_redirects=False,
            )

            assert response.status_code == 302  # Redirect with error flash


class TestUpdateProfile:
    """Tests for /profile/update endpoint"""

    def test_update_profile_success(self, authenticated_client, test_user):
        """Test successful profile update"""
        data = {
            "username": "newusername",
            "email": "newemail@example.com",
            "bio": "New bio",
        }
        response = authenticated_client.post(
            "/profile/update", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect after success

    def test_update_profile_duplicate_username(
        self, authenticated_client, test_user, test_user2
    ):
        """Test profile update with duplicate username"""
        data = {"username": test_user2.username, "email": "unique@example.com"}
        response = authenticated_client.post(
            "/profile/update", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect with error flash

    def test_update_profile_duplicate_email(
        self, authenticated_client, test_user, test_user2
    ):
        """Test profile update with duplicate email"""
        data = {"username": "uniqueuser", "email": test_user2.email}
        response = authenticated_client.post(
            "/profile/update", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect with error flash


class TestAddSkill:
    """Tests for /profile/skills/add endpoint"""

    def test_add_skill_success(self, authenticated_client, test_user):
        """Test successfully adding a skill"""
        data = {"instrument": "Python", "level": "Expert", "years": "5"}
        response = authenticated_client.post(
            "/profile/skills/add", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect after success

    def test_add_skill_missing_fields(self, authenticated_client):
        """Test adding skill with missing fields"""
        data = {"instrument": "Python"}
        response = authenticated_client.post(
            "/profile/skills/add", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect with error flash

    def test_add_skill_invalid_level(self, authenticated_client):
        """Test adding skill with invalid level"""
        data = {"instrument": "Python", "level": "InvalidLevel", "years": "5"}
        response = authenticated_client.post(
            "/profile/skills/add", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect with error flash

    def test_add_skill_duplicate(
        self, authenticated_client, test_user, test_skill, test_user_skill
    ):
        """Test adding duplicate skill"""
        data = {"instrument": test_skill.name, "level": "Expert", "years": "5"}
        response = authenticated_client.post(
            "/profile/skills/add", data=data, follow_redirects=False
        )

        assert response.status_code == 302  # Redirect with error flash


class TestDeleteSkill:
    """Tests for /profile/skills/delete/<id> endpoint"""

    def test_delete_skill_success(
        self, authenticated_client, test_user, test_skill, test_user_skill
    ):
        """Test successfully deleting a skill"""
        response = authenticated_client.post(
            f"/profile/skills/delete/{test_user_skill.id}",
            follow_redirects=False,
        )

        assert response.status_code == 302  # Redirect after success

    def test_delete_nonexistent_skill(self, authenticated_client, test_user):
        """Test deleting nonexistent skill"""
        response = authenticated_client.post(
            "/profile/skills/delete/99999", follow_redirects=False
        )

        assert response.status_code == 302  # Redirect with error flash

    def test_delete_other_user_skill(
        self, authenticated_client, test_user, test_user2, test_skill
    ):
        """Test deleting another user's skill"""
        from app.extensions import db

        # Create skill for test_user2
        other_user_skill = UserSkill(
            user_id=test_user2.id,
            skill_id=test_skill.id,
            level="Expert",
            years=5,
        )
        db.session.add(other_user_skill)
        db.session.commit()

        response = authenticated_client.post(
            f"/profile/skills/delete/{other_user_skill.id}",
            follow_redirects=False,
        )

        assert response.status_code == 302  # Redirect with error flash
