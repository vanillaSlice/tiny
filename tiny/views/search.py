from flask import Blueprint, jsonify, redirect, render_template, request, url_for

search = Blueprint("search", __name__, url_prefix="/search")

@search.route("", methods=["GET", "POST"], defaults={"query": ""})
@search.route("<query>", methods=["GET", "POST"])
def results(query):
    if request.method == "POST":
        results = []
        return jsonify(results)
    return render_template("search/index.html")
