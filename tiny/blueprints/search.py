"""
Exports search routes.
"""

from flask import Blueprint, jsonify, render_template, request

from tiny.helpers import is_int
from tiny.models import Post

search = Blueprint("search", __name__, url_prefix="/search")

@search.route("", methods=["GET"])
def index():
    return render_template("search/index.html")

@search.route("/query", methods=["GET"])
def query():
    # get query parameters
    terms = request.args.get("terms", "")
    size = request.args.get("size", 10)
    offset = request.args.get("offset", 0)

    # validate query parameters
    if not is_int(size):
        return jsonify({"error message": "invalid size {}".format(size)}), 400
    if not is_int(offset):
        return jsonify({"error message": "invalid offset {}".format(offset)}), 400

    # normalise query parameters
    size = int(size)
    # cap number of posts to return
    size = 100 if size > 100 else size
    offset = int(offset)

    query_set = Post.objects
    if terms:
        # get posts containing terms (if given)
        query_set = query_set.search_text(terms).order_by("$text_score")
    else:
        # otherwise get all posts
        query_set = query_set.order_by("-created")

    # make sure to exclude the actual content
    results = query_set.exclude("content").skip(offset).limit(size)

    # serialize the posts
    posts = []
    for result in results:
        posts.append(result.serialize())

    return jsonify(posts)
