from flask import render_template, request
from .search import handle_search
from app.search import bp


@bp.route('/', methods=['GET'])
@bp.get("/all")
def search_all():
    """Render search page with results"""
    query = request.args.get("q", "").strip()
    search_data = handle_search(query)
    
    return render_template(
        "search/all.html",
        q=search_data["q"],
        users=search_data["users"],
        projects=search_data["projects"],
        skills=search_data["skills"],
        counts=search_data["counts"],
        preview_limit=search_data["preview_limit"],
        message=search_data.get("message", "")
    )
