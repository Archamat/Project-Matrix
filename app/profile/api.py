from flask import request, jsonify
from flask_login import login_required, current_user
from . import profile_api
from app.profile.profile import (
    handle_update_profile,
    handle_avatar_upload,
    handle_skill_add,
    handle_skill_delete,
)
from app.aws import upload_fileobj_private
from app.aws.s3 import presigned_get_url

IMAGE_MIME_ALLOW = {"image/jpeg", "image/png", "image/webp", "image/gif"}


# ==================== PROFILE UPDATE ====================
@profile_api.route("/update", methods=["POST"])
@login_required
def update_profile():
    """API endpoint for updating profile info"""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()

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
            return jsonify(
                {"success": False, "message": "No file provided"}
            ), 400

        if file.mimetype not in IMAGE_MIME_ALLOW:
            return jsonify(
                {"success": False, "message": "Only JPG/PNG/WEBP/GIF allowed"}
            ), 400

        result = upload_fileobj_private(
            file, prefix=f"avatars/{current_user.id}/"
        )

        updated_user = handle_avatar_upload(current_user, result["key"])

        avatar_url = presigned_get_url(
            updated_user.avatar_url, expires_in=3600
        )

        return jsonify(
            {
                "success": True,
                "message": "Avatar uploaded successfully",
                "avatar_url": avatar_url,
            }
        ), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ==================== SKILLS MANAGEMENT ====================
@profile_api.route("/skills", methods=["POST"])
@login_required
def add_skill():
    """API endpoint for adding a skill"""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()

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

        return jsonify(
            {"success": True, "message": "Skill removed successfully"}
        ), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception:
        return jsonify({"success": False, "message": "Server error"}), 500
