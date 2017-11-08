from flask import Blueprint, render_template

search = Blueprint("search", __name__, url_prefix="/search")

@search.route("/")
def index():
    return render_template("search/index.html")
