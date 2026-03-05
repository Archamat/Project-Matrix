"""
Tests for profile view routes
"""

from unittest.mock import patch
from io import BytesIO
import importlib

from app.profile.models import UserSkill


class TestShowProfile:
    """Tests for /profile route (own profile)"""

    def test_show_profile(self, authenticated_client, test_user):
        """Test viewing own profile"""
        response = authenticated_client.get("/profile/")
        assert response.status_code == 200

    def test_show_profile_unauthenticated(self, client):
        """Test that unauthenticated users are redirected"""
        response = client.get("/profile/")
        assert response.status_code in (302, 401)


class TestViewProfile:
    """Tests for /profile/<user_id> route"""

    def test_view_profile(self, authenticated_client, test_user):
        """Test viewing a user profile"""
        response = authenticated_client.get(f"/profile/{test_user.id}")
        assert response.status_code == 200

    def test_view_nonexistent_profile(self, authenticated_client):
        """Test viewing a profile that doesn't exist"""
        response = authenticated_client.get("/profile/9999")
        assert response.status_code == 404

    def test_view_profile_unauthenticated(self, client, test_user):
        """Test that unauthenticated users are redirected"""
        response = client.get(f"/profile/{test_user.id}")
        assert response.status_code in (302, 401)


class TestUploadAvatar:
    """Tests for avatar upload route"""

    def test_upload_avatar_get(self, authenticated_client):
        """Test GET request for avatar upload page"""
        response = authenticated_client.get("/profile/avatar")
        assert response.status_code == 200

    @patch("app.profile.api.upload_to_s3")
    def test_upload_avatar_success(
        self, mock_upload, authenticated_client, test_user
    ):
        """Test successful avatar upload"""
        mock_upload.return_value = "avatars/test/avatar.jpg"

        data = {"avatar": (BytesIO(b"fake image data"), "avatar.jpg")}
        response = authenticated_client.post(
            "/profile/avatar",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_upload_avatar_no_file(self, authenticated_client):
        """Test avatar upload with no file"""
        response = authenticated_client.post(
            "/profile/avatar",
            data={},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code in (200, 400)


class TestUpdateProfile:
    """Tests for profile update route"""

    def test_update_profile_success(self, authenticated_client, test_user):
        """Test successful profile update"""
        data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "bio": "Updated bio",
            "contact_info": "Updated contact",
        }
        response = authenticated_client.post(
            "/profile/edit",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_update_profile_missing_fields(self, authenticated_client):
        """Test profile update with missing required fields"""
        data = {"bio": "Only bio"}
        response = authenticated_client.post(
            "/profile/edit",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code in (200, 400)

    def test_update_profile_get(self, authenticated_client):
        """Test GET request for profile edit page"""
        response = authenticated_client.get("/profile/edit")
        assert response.status_code == 200


class TestAddSkill:
    """Tests for skill addition route"""

    def test_add_skill_success(self, authenticated_client, test_user):
        """Test successfully adding a skill"""
        data = {
            "skill_name": "Python",
            "level": "Intermediate",
            "years": "3",
        }
        response = authenticated_client.post(
            "/profile/skills/add",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_add_skill_missing_name(self, authenticated_client):
        """Test adding skill without name"""
        data = {"level": "Intermediate", "years": "3"}
        response = authenticated_client.post(
            "/profile/skills/add",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code in (200, 400)

    def test_add_skill_invalid_level(self, authenticated_client):
        """Test adding skill with invalid level"""
        data = {
            "skill_name": "Python",
            "level": "InvalidLevel",
            "years": "3",
        }
        response = authenticated_client.post(
            "/profile/skills/add",
            data=data,
            follow_redirects=True,
        )
        assert response.status_code in (200, 400)


class TestDeleteSkill:
    """Tests for skill deletion route"""

    def test_delete_skill_success(self, authenticated_client, test_user, db):
        """Test successfully deleting a skill"""
        from app.profile.profile import handle_skill_add

        user_skill = handle_skill_add(test_user, "Python", "Intermediate", 3)
        db.session.commit()

        response = authenticated_client.post(
            f"/profile/skills/{user_skill.id}/delete",
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_delete_nonexistent_skill(self, authenticated_client):
        """Test deleting a skill that doesn't exist"""
        response = authenticated_client.post(
            "/profile/skills/9999/delete",
            follow_redirects=True,
        )
        assert response.status_code in (200, 404)
