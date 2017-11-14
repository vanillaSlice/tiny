"""
Contins post routes.
"""

from datetime import datetime

from bson.objectid import ObjectId
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from tiny.helpers import sign_in_required
from tiny.forms import NewPostForm
from tiny.models import Post, User

post = Blueprint("post", __name__, url_prefix="/post")

# new
# search
# show

@post.route("/new", methods=["GET", "POST"])
@sign_in_required
def new():
    # parse the form
    form = NewPostForm(request.form)

    # render new post form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("post/new.html", form=form)

    # save new post
    Post(author=User.objects(id=ObjectId(session.get("user_id"))).first(),
         title=form.title.data,
         introduction=form.introduction.data,
         image_url=form.image_url.data,
         content=form.content.data,
         published=datetime.now()).save()

    # notify user
    flash("Post successfully created", "success")

    # redirect to home page
    return redirect(url_for("home.index"))

@post.route("/search", methods=["GET"])
def search():
    size = int(request.args.get("size", 12))
    offset = int(request.args.get("offset", 0))
    order = request.args.get("order", "true").lower() == "true"
    query_set = Post.objects
    if order:
        query_set = query_set.order_by("-published")
    results = query_set.skip(offset).limit(size)
    posts = []
    for result in results:
        posts.append(result.serialize())
    return jsonify(posts)


@post.route("/get", methods=["GET"])
def get():
    posts = []
    for i in range(0, 12):
        post = Post(title="Post Title")
        posts.append(post.serialize())
    return jsonify(posts)
