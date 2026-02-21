"""
Tests for profile API endpoints
"""

import json
from unittest.mock import patch
from io import BytesIO
import importlib
from app.profile.models import UserSkill


class TestUpdateProfileAPI:
    """Tests for /api/profile/update endpoint"""

    def test_update_profile_requires_login(self, client):
        """Test that profile update requires authentication"""
        response = client.post("/api/profile/update", follow_redirects=False)
        assert response.status_code == 302  # Redirect to login

    def test_update_profile_success_json(
        self, authenticated_client, test_user
    ):
        """Test successful profile update via JSON"""
        data = {
            "username": "newusername",
            "email": "newemail@example.com",
            "bio": "New bio",
            "contact_info": "New contact",
        }
        response = authenticated_client.post(
            "/api/profile/update",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True

    def test_update_profile_success_form(
        self, authenticated_client, test_user
    ):
        """Test successful profile update via form data"""
        data = {
            "username": "newusername",
            "email": "newemail@example.com",
            "bio": "New bio",
        }
        response = authenticated_client.post("/api/profile/update", data=data)

        assert response.status_code == 200

    def test_update_profile_duplicate_username(
        self, authenticated_client, test_user, test_user2
    ):
        """Test profile update with duplicate username"""
        data = {"username": test_user2.username, "email": "unique@example.com"}
        response = authenticated_client.post(
            "/api/profile/update",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400


class TestUploadAvatarAPI:
    """Tests for /api/profile/avatar endpoint"""

    def test_upload_avatar_success(self, authenticated_client, test_user, app):
        """Test successful avatar upload"""
        api_module = importlib.import_module("app.profile.api")
        with patch.object(
            api_module, "upload_fileobj_private"
        ) as mock_upload, patch.object(
            api_module, "presigned_get_url"
        ) as mock_presigned:
            mock_upload.return_value = {"key": "avatars/1/test.jpg"}
            mock_presigned.return_value = "https://example.com/signed-url"

            data = {
                "avatar_file": (
                    BytesIO(b"fake image data"),
                    "test.jpg",
                    "image/jpeg",
                )
            }
            response = authenticated_client.post(
                "/api/profile/avatar",
                data=data,
                content_type="multipart/form-data",
            )

            assert response.status_code == 200
            result = json.loads(response.data)
            assert result["success"] is True
            assert "avatar_url" in result

    def test_upload_avatar_no_file(self, authenticated_client):
        """Test avatar upload without file"""
        response = authenticated_client.post(
            "/api/profile/avatar", data={}, content_type="multipart/form-data"
        )

        assert response.status_code == 400

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
            "/api/profile/avatar",
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_upload_avatar_upload_failure(self, authenticated_client, app):
        """Test avatar upload when S3 upload fails"""
        api_module = importlib.import_module("app.profile.api")
        with patch.object(api_module, "upload_fileobj_private") as mock_upload:
            mock_upload.side_effect = Exception("S3 upload failed")

            data = {
                "avatar_file": (
                    BytesIO(b"fake image data"),
                    "test.jpg",
                    "image/jpeg",
                )
            }
            response = authenticated_client.post(
                "/api/profile/avatar",
                data=data,
                content_type="multipart/form-data",
            )

            assert response.status_code == 500


class TestAddSkillAPI:
    """Tests for /api/profile/skills endpoint"""

    def test_add_skill_success_json(self, authenticated_client, test_user):
        """Test successfully adding a skill via JSON"""
        data = {"instrument": "Python", "level": "Expert", "years": 5}
        response = authenticated_client.post(
            "/api/profile/skills",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 201

    def test_add_skill_success_form(self, authenticated_client, test_user):
        """Test successfully adding a skill via form data"""
        data = {"instrument": "JavaScript", "level": "Expert", "years": "5"}
        response = authenticated_client.post("/api/profile/skills", data=data)

        assert response.status_code == 201

    def test_add_skill_missing_fields(self, authenticated_client):
        """Test adding skill with missing required fields"""
        data = {"instrument": "Python"}
        response = authenticated_client.post(
            "/api/profile/skills",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_add_skill_invalid_level(self, authenticated_client):
        """Test adding skill with invalid level"""
        data = {"instrument": "Python", "level": "InvalidLevel", "years": 5}
        response = authenticated_client.post(
            "/api/profile/skills",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_add_skill_duplicate(
        self, authenticated_client, test_user, test_skill, test_user_skill
    ):
        """Test adding duplicate skill"""
        data = {"instrument": test_skill.name, "level": "Expert", "years": 5}
        response = authenticated_client.post(
            "/api/profile/skills",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400


class TestDeleteSkillAPI:
    """Tests for DELETE /api/profile/skills/<id> endpoint"""

    def test_delete_skill_success(
        self, authenticated_client, test_user, test_skill, test_user_skill
    ):
        """Test successfully deleting a skill"""
        response = authenticated_client.delete(
            f"/api/profile/skills/{test_user_skill.id}"
        )

        assert response.status_code == 200

    def test_delete_nonexistent_skill(self, authenticated_client, test_user):
        """Test deleting nonexistent skill"""
        response = authenticated_client.delete("/api/profile/skills/99999")

        assert response.status_code == 404

    def test_delete_other_user_skill(
        self, authenticated_client, test_user, test_user2, test_skill
    ):
        """Test deleting another user's skill returns 404 (skill not found for this user)"""
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

        response = authenticated_client.delete(
            f"/api/profile/skills/{other_user_skill.id}"
        )

        # The API returns 404 when trying to delete another user's skill
        # because it filters by current_user.id
        assert response.status_code == 404
