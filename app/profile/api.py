from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.profile.profile import (
    handle_update_profile,
    handle_avatar_upload,
    handle_demo_upload,
    handle_demo_delete,
    handle_skill_add,
    handle_skill_delete,
)
from app.aws import upload_fileobj_private
from app.aws.s3 import presigned_get_url
from app.profile.profile_database_manager import ProfileDatabaseManager

# Constants
AUDIO_MIME_ALLOW = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/ogg",
    "audio/webm",
    "audio/x-wav",
    "audio/wave",
    "audio/flac",
}
IMAGE_MIME_ALLOW = {"image/jpeg", "image/png", "image/webp", "image/gif"}

profile_api = Blueprint("profile_api", __name__, url_prefix="/api/profile")


# ==================== PROFILE UPDATE ====================
@profile_api.route("/update", methods=["POST"])
@login_required
def update_profile():
    """API endpoint for updating profile info"""
    try:
        data = request.get_json() or request.form.to_dict()

        updated_user = handle_update_profile(current_user, data)

        return jsonify(
            {
                "success": True,
                "message": "Profile updated successfully",
                "user": {
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "bio": updated_user.bio,
                    "contact_info": updated_user.contact_info,
                },
            }
        ), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


# ==================== AVATAR UPLOAD ====================
@profile_api.route("/avatar", methods=["POST"])
@login_required
def upload_avatar():
    """API endpoint for avatar upload"""
    try:
        file = request.files.get("avatar_file")

        if not file or file.filename == "":
            return jsonify({"success": False, "message": "No file provided"}), 400

        if file.mimetype not in IMAGE_MIME_ALLOW:
            return jsonify(
                {"success": False, "message": "Only JPG/PNG/WEBP/GIF allowed"}
            ), 400

        result = upload_fileobj_private(file, prefix=f"avatars/{current_user.id}/")

        updated_user = handle_avatar_upload(current_user, result["key"])

        avatar_url = presigned_get_url(updated_user.avatar_url, expires_in=3600)

        return jsonify(
            {
                "success": True,
                "message": "Avatar uploaded successfully",
                "avatar_url": avatar_url,
            }
        ), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== DEMO MANAGEMENT ====================
@profile_api.route("/demo", methods=["POST"])
@login_required
def upload_demo():
    """API endpoint for demo upload"""
    try:
        file = request.files.get("demo_file")
        title = request.form.get("title", "").strip()

        if not file or file.filename == "":
            return jsonify({"success": False, "message": "No file provided"}), 400

        if file.mimetype not in AUDIO_MIME_ALLOW:
            return jsonify({"success": False, "message": "Unsupported audio type"}), 400

        result = upload_fileobj_private(file, prefix=f"demos/{current_user.id}/")

        demo = handle_demo_upload(
            current_user, result["key"], title or file.filename, file.mimetype
        )

        return jsonify(
            {
                "success": True,
                "message": "Demo uploaded successfully",
                "demo": {"id": demo.id, "title": demo.title, "mime": demo.mime},
            }
        ), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@profile_api.route("/demo/<int:demo_id>", methods=["DELETE"])
@login_required
def delete_demo(demo_id):
    """API endpoint for demo deletion"""
    try:
        handle_demo_delete(current_user, demo_id)

        return jsonify({"success": True, "message": "Demo deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@profile_api.route("/demos", methods=["GET"])
@login_required
def list_demos():
    """API endpoint to list all user demos"""
    try:
        demos = ProfileDatabaseManager.get_user_demos(current_user.id)

        items = []
        for demo in demos:
            try:
                url = presigned_get_url(demo.key, expires_in=3600)
            except Exception:
                url = None

            items.append(demo.to_dict(include_url=True, presigned_url=url))

        return jsonify({"success": True, "demos": items}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== SKILLS MANAGEMENT ====================
@profile_api.route("/skills", methods=["POST"])
@login_required
def add_skill():
    """API endpoint for adding a skill"""
    try:
        data = request.get_json() or request.form.to_dict()

        skill_name = data.get("instrument", "").strip()
        level = data.get("level")
        years = data.get("years", 0)

        user_skill = handle_skill_add(current_user, skill_name, level, years)

        return jsonify(
            {
                "success": True,
                "message": f"Added skill: {skill_name}",
                "skill": {
                    "id": user_skill.id,
                    "name": user_skill.skill.name,
                    "level": user_skill.level,
                    "years": user_skill.years,
                },
            }
        ), 201

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500


@profile_api.route("/skills/<int:skill_id>", methods=["DELETE"])
@login_required
def delete_skill(skill_id):
    """API endpoint for removing a skill"""
    try:
        handle_skill_delete(current_user, skill_id)

        return jsonify({"success": True, "message": "Skill removed successfully"}), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500
