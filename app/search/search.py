from .search_database_manager import SearchDatabaseManager


def handle_search(query):
    """
    Handle search logic and return data

    Args:
        query: Search query string

    Returns:
        dict: Search results with users, projects, skills, counts, and metadata
    """
    PREVIEW = 5
    q = (query or "").strip()

    if not q:
        return {
            "q": "",
            "users": [],
            "projects": [],
            "skills": [],
            "counts": {"users": 0, "projects": 0, "skills": 0},
            "preview_limit": PREVIEW,
            "message": "Type something to search.",
        }

    results = SearchDatabaseManager.search_all(q, preview_limit=PREVIEW)

    return {
        "q": q,
        "users": results["users"],
        "projects": results["projects"],
        "skills": results["skills"],
        "counts": results["counts"],
        "preview_limit": PREVIEW,
    }
