from .search import handle_search
from app.search import bp

@bp.route('/', methods=['GET'])
@bp.get("/all")
def search_all():
    return handle_search()
