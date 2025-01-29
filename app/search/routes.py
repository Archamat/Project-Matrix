from flask import render_template, request
from app.search import bp

@bp.route('/', methods=['GET'])
def search():
    query = request.args.get('q', '')
    return render_template('search/results.html', query=query)