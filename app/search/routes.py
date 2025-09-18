from flask import Blueprint, render_template, request
from app.search import bp
from flask_login import login_required
from sqlalchemy import or_, func
from app.search import bp
from app.auth.models import User
from app.profile.models import Skill, UserSkill
from app.projects.models import Project  

@bp.route('/', methods=['GET'])
# --- USERS ---
@bp.get("/users")
def search_users():
    q = (request.args.get("q") or "").strip()
    skill = (request.args.get("skill") or "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            User.username.ilike(like),
            User.email.ilike(like),
            func.coalesce(User.bio, "").ilike(like),
        ))
    if skill:
        query = (query.join(User.skills)
                     .join(UserSkill.skill)
                     .filter(Skill.name.ilike(skill)))

    query = query.distinct(User.id).order_by(User.username.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("search/users.html",
                           users=pagination.items,
                           pagination=pagination,
                           q=q, skill=skill)

# --- PROJECTS ---
@bp.get("/projects")
def search_projects():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    query = Project.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Project.name.ilike(like),
            func.coalesce(Project.description, "").ilike(like),
        ))

    pagination = query.order_by(Project.updated_at.desc()) \
                      .paginate(page=page, per_page=per_page, error_out=False)

    return render_template("search/projects.html",
                           projects=pagination.items,
                           pagination=pagination,
                           q=q)

# --- SKILLS ---
@bp.get("/skills")
def search_skills():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    query = Skill.query
    if q:
        like = f"%{q}%"
        query = query.filter(Skill.name.ilike(like))

    pagination = query.order_by(Skill.name.asc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("search/skills.html",
                           skills=pagination.items,
                           pagination=pagination,
                           q=q)

@bp.get("/all")
def search_all():
    q = (request.args.get("q") or "").strip()
    if not q:
        return render_template(
            "search/all.html",
            q="",
            users=[], projects=[], skills=[],
            counts={"users": 0, "projects": 0, "skills": 0},
            preview_limit=5
        )

    like = f"%{q}%"
    PREVIEW = 5

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


