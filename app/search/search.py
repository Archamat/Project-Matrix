from flask import render_template, request
from sqlalchemy import func
from app.auth.models import User
from app.profile.models import Skill
from app.projects.models import Project  


def handle_search():
    q = (request.args.get("q") or "").strip()
    PREVIEW = 5
    if not q:
        return render_template(
            "search/all.html",
            q="",
            users=[],
            projects=[],
            skills=[],
            counts={"users": 0, "projects": 0, "skills": 0},
            preview_limit=PREVIEW,
            message="Type something to search."
        )

    like = f"%{q}%"

    # Users
    users_q = User.query.filter(
        (User.username.ilike(like)) | (func.coalesce(User.bio, "").ilike(like))
    )
    users_preview = users_q.order_by(User.username.asc()).limit(PREVIEW).all()
    users_count = users_q.count()

    # Projects (no created_at)
    projects_q = Project.query.filter(
        (Project.name.ilike(like)) | (func.coalesce(Project.description, "").ilike(like))
    )
    projects_preview = projects_q.order_by(Project.name.asc()).limit(PREVIEW).all()
    projects_count = projects_q.count()

    # Skills
    skills_q = Skill.query.filter(Skill.name.ilike(like))
    skills_preview = skills_q.order_by(Skill.name.asc()).limit(PREVIEW).all()
    skills_count = skills_q.count()

    return render_template(
        "search/all.html",
        q=q,
        users=users_preview,
        projects=projects_preview,
        skills=skills_preview,
        counts={"users": users_count, "projects": projects_count, "skills": skills_count},
        preview_limit=PREVIEW,
    )