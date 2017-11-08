from flask import Blueprint, render_template

post = Blueprint("post", __name__, url_prefix="/post")

@post.route("/new")
def new():
    return render_template("post/new.html")
