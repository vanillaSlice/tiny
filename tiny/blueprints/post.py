"""
Exports post routes.
"""

from datetime import datetime

from bson.objectid import ObjectId
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from tiny.helpers import is_int, is_valid_object_id, sign_in_required
from tiny.forms import CommentForm, PostForm
from tiny.models import Comment, Post, User

post = Blueprint("post", __name__, url_prefix="/post")

@post.route("/create", methods=["GET", "POST"])
@sign_in_required
def create():
    # parse the form
    form = PostForm(request.form)

    # render create post form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("post/create.html", form=form)

    # create new post
    new_post = Post(author=User.objects(id=ObjectId(session.get("user_id"))).first(),
                    title=form.title.data,
                    preview=form.preview.data,
                    content=form.content.data)

    # add image url if not blank
    image_url = form.image_url.data.strip()
    if image_url:
        new_post.image_url = image_url

    # save new post
    new_post.save()

    # notify user
    flash("Post successfully created", "success")

    # redirect to post page
    return redirect(url_for("post.show", post_id=str(new_post.id)))

@post.route("/<post_id>/show", methods=["GET"])
def show(post_id):
    # try to find post with given id
    if is_valid_object_id(post_id):
        selected_post = Post.objects(id=ObjectId(post_id)).first()
    else:
        selected_post = None

    # couldn't find post - redirect to home page
    if selected_post is None:
        flash("Oops - we couldn't find that post", "danger")
        return redirect(url_for("home.index"))

    # render post
    return render_template("post/show.html", post=selected_post)

@post.route("/<post_id>/update", methods=["GET", "POST"])
@sign_in_required
def update(post_id):
    # try to find post with given id
    if is_valid_object_id(post_id):
        selected_post = Post.objects(id=ObjectId(post_id)).first()
    else:
        selected_post = None

    # couldn't find post - redirect to home page
    if selected_post is None:
        flash("Oops - we couldn't find that post", "danger")
        return redirect(url_for("home.index"))

    current_user = User.objects(id=ObjectId(session.get("user_id"))).first()

    # make sure user is the author
    if selected_post.author.id != current_user.id:
        flash("Can't update a post that you are not the author of", "danger")
        return redirect(url_for("post.show", post_id=post_id))

    # parse the form
    form = PostForm(request.form)

    # render update post form with existing values if GET request
    if request.method == "GET":
        form.title.data = selected_post.title
        form.preview.data = selected_post.preview
        form.image_url.data = selected_post.image_url
        form.content.data = selected_post.content
        return render_template("post/update.html", form=form, post_id=post_id)

    # render update post form if submitted form is invalid
    if not form.validate():
        return render_template("post/update.html", form=form)

    # normalise image url
    form.image_url.data = form.image_url.data.strip()

    # update the post information
    selected_post.title = form.title.data
    selected_post.preview = form.preview.data
    if form.image_url.data:
        selected_post.image_url = form.image_url.data
    selected_post.content = form.content.data
    selected_post.last_updated = datetime.now()
    selected_post.save()

    # notify the user
    flash("Post successfully updated", "success")

    # redirect back to settings page
    return redirect(url_for("post.show", post_id=post_id))

@post.route("/<post_id>/delete", methods=["GET", "POST"])
@sign_in_required
def delete(post_id):
    # try to find post with given id
    if is_valid_object_id(post_id):
        selected_post = Post.objects(id=ObjectId(post_id)).first()
    else:
        selected_post = None

    # couldn't find post - redirect to home page
    if selected_post is None:
        flash("Oops - we couldn't find that post", "danger")
        return redirect(url_for("home.index"))

    current_user = User.objects(id=ObjectId(session.get("user_id"))).first()

    # make sure user is the author
    if selected_post.author.id != current_user.id:
        flash("Can't delete a post that you are not the author of", "danger")
        return redirect(url_for("post.show", post_id=post_id))

    # render delete page if GET request
    if request.method == "GET":
        return render_template("post/delete.html", post=selected_post)

    # delete the post
    selected_post.delete()

    # notify user
    flash("Successfully deleted post", "success")

    # redirect back to homepage
    return redirect(url_for("home.index"))

@post.route("/<post_id>/comments", methods=["GET"])
def comments(post_id):
    # get query parameters
    size = request.args.get("size", 10)
    offset = request.args.get("offset", 0)
    order = request.args.get("order", "true").lower() == "true"

    # validate query parameters
    if not is_valid_object_id(post_id):
        return jsonify({"error message": "invalid post id {}".format(post_id)}), 400
    if not is_int(size):
        return jsonify({"error message": "invalid size {}".format(size)}), 400
    if not is_int(offset):
        return jsonify({"error message": "invalid offset {}".format(offset)}), 400

    # normalise query parameters
    post_id = ObjectId(post_id)
    size = int(size)
    # cap number of comments to return
    size = 100 if size > 100 else size
    offset = int(offset)

    # query for post's comments (making sure to exclude the post itself)
    query_set = Comment.objects(post=post_id).exclude("post")
    if order:
        query_set = query_set.order_by("created")
    results = query_set.skip(offset).limit(size)

    # serialize the posts
    user_posts = []
    for result in results:
        user_posts.append(result.serialize())

    return jsonify(user_posts)

@post.route("/<post_id>/comment", methods=["POST"])
@sign_in_required
def comment(post_id):
    # validate post id
    if not is_valid_object_id(post_id):
        return jsonify({"error message": "invalid post id {}".format(post_id)}), 400

    # try to find post
    selected_post = Post.objects(id=ObjectId(post_id)).first()

    # couldn't find post
    if selected_post is None:
        return jsonify({"error message": "post with id {} does not exist".format(post_id)}), 400

    # parse the form
    form = CommentForm(request.form)

    # form is not valid so return error
    if not form.validate():
        return jsonify({"error message": "invalid text {}".format(str(form.text.errors))}), 400

    # create the comment
    Comment(author=User.objects(id=ObjectId(session.get("user_id"))).first(),
            post=selected_post,
            text=form.text.data).save()

    return jsonify({"success": "true"}), 200
