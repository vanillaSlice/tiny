"""
Exports search routes.
"""

from flask import Blueprint, jsonify, render_template, request

from tiny.helpers import request_wants_json, search_posts, serialize

search = Blueprint('search', __name__, url_prefix='/search')

@search.route('/', methods=['GET'])
def index():
    """
    Search route.
    """

    # not json so just render search page
    if not request_wants_json():
        return render_template('search/index.html')

    # get query parameters
    terms = request.args.get('terms', '', type=str)
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 12, type=int)

    # search for posts (making sure to exclude the actual content)
    results = search_posts(search_text=terms,
                           exclude=['content'],
                           order_by=['$text_score'],
                           skip=skip,
                           limit=limit)

    return jsonify(serialize(results))
