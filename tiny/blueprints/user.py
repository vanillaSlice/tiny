"""
Exports user routes.
"""

from bson.objectid import ObjectId
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from passlib.hash import sha256_crypt

from tiny.forms import SignInForm, SignUpForm, UpdatePasswordForm, UpdateProfileForm
from tiny.helpers import is_int, is_valid_object_id, sign_in_required
from tiny.models import Post, User

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    # redirect to home page if already signed in
    if session.get("user_id"):
        return redirect(url_for("home.index"))

    # parse the form
    form = SignUpForm(request.form)

    # render sign up form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("user/sign_up.html", form=form)

    # check if there is an existing account with this email
    if User.objects(email=form.email.data):
        form.email.errors.append("There is already an account with this email")
        return render_template("user/sign_up.html", form=form)

    # save new user
    new_user = User(email=form.email.data,
                    password=sha256_crypt.hash(form.password.data),
                    display_name=form.display_name.data).save()

    # clear any session data that may be lingering
    session.clear()

    # make sure we store user id and avatar url in session
    session["user_id"] = str(new_user.id)
    session["avatar_url"] = new_user.avatar_url

    # notify user
    flash("Profile successfully created", "success")

    # redirect to user's profile page
    return redirect(url_for("user.show", user_id=session["user_id"]))

@user.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    # redirect to home page if already signed in
    if session.get("user_id"):
        return redirect(url_for("home.index"))

    # parse the form
    form = SignInForm(request.form)

    # render sign in form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("user/sign_in.html", form=form)

    # try to find the user
    current_user = User.objects(email=form.email.data).first()

    # check if there is an existing account with this email
    if not current_user:
        form.email.errors.append("There is no account with this email")
        return render_template("user/sign_in.html", form=form)

    # check password is correct
    if not sha256_crypt.verify(form.password.data, current_user.password):
        form.password.errors.append("Incorrect password")
        return render_template("user/sign_in.html", form=form)

    # clear any session data that may be lingering
    session.clear()

    # make sure we store user id and avatar url in session
    session["user_id"] = str(current_user.id)
    session["avatar_url"] = current_user.avatar_url

    # notify user
    flash("Successfully signed in", "success")

    # redirect to next screen (if there is one) or home page
    return redirect(request.args.get("next") or url_for("home.index"))

@user.route("/sign-out", methods=["GET", "POST"])
def sign_out():
    # clear session data only if POST request
    if request.method == "POST":
        session.clear()

    # render sign out page
    return render_template("user/sign_out.html")

@user.route("/<user_id>/show", methods=["GET"])
def show(user_id):
    # try to find user with given id (making sure to exclude email and password)
    if is_valid_object_id(user_id):
        selected_user = User.objects(id=ObjectId(user_id)).exclude("email", "password").first()
    else:
        selected_user = None

    # couldn't find user - redirect to home page
    if selected_user is None:
        flash("Oops - we couldn't find that profile", "danger")
        return redirect(url_for("home.index"))

    # render user's profile page
    return render_template("user/show.html", user=selected_user)

@user.route("/settings", methods=["GET"])
@sign_in_required
def settings():
    return render_template("user/settings.html")

@user.route("/update-profile", methods=["GET", "POST"])
@sign_in_required
def update_profile():
    current_user = User.objects(id=ObjectId(session.get("user_id"))).first()

    # parse the form
    form = UpdateProfileForm(request.form)

    # render update profile form with existing values if GET request
    if request.method == "GET":
        form.display_name.data = current_user.display_name
        form.avatar_url.data = current_user.avatar_url
        form.bio.data = current_user.bio
        return render_template("user/update_profile.html", form=form)

    # render update profile form if submitted form is invalid
    if not form.validate():
        return render_template("user/update_profile.html", form=form)

    # normalise avatar url
    form.avatar_url.data = form.avatar_url.data.strip()

    # update the user information
    current_user.display_name = form.display_name.data
    if form.avatar_url.data:
        current_user.avatar_url = form.avatar_url.data
    current_user.bio = form.bio.data
    current_user.save()

    # make sure we store the avatar url in session
    session["avatar_url"] = current_user.avatar_url

    # notify the user
    flash("Profile successfully updated", "success")

    # redirect back to settings page
    return redirect(url_for("user.settings"))

@user.route("/update-password", methods=["GET", "POST"])
@sign_in_required
def update_password():
    # parse the form
    form = UpdatePasswordForm(request.form)

    # render update password form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("user/update_password.html", form=form)

    current_user = User.objects(id=ObjectId(session.get("user_id"))).first()

    # check current password is correct
    if not sha256_crypt.verify(form.current_password.data, current_user.password):
        form.current_password.errors.append("Incorrect password")
        return render_template("user/update_password.html", form=form)

    # update password
    current_user.password = sha256_crypt.hash(form.new_password.data)
    current_user.save()

    # notify the user
    flash("Password successfully updated", "success")

    # redirect back to settings page
    return redirect(url_for("user.settings"))

@user.route("/delete", methods=["GET", "POST"])
@sign_in_required
def delete():
    # render delete page if GET request
    if request.method == "GET":
        return render_template("user/delete.html")

    # delete the current user
    current_user = User.objects(id=ObjectId(session.get("user_id"))).first()
    if current_user:
        current_user.delete()

    # make sure we clear the session
    session.clear()

    # notify user
    flash("Successfully deleted account", "success")

    # redirect back to homepage
    return redirect(url_for("home.index"))

@user.route("/<user_id>/posts", methods=["GET"])
def posts(user_id):
    # get query parameters
    size = request.args.get("size", 10)
    offset = request.args.get("offset", 0)

    # validate query parameters
    if not is_valid_object_id(user_id):
        return jsonify({"error message": "invalid author id {}".format(user_id)}), 400
    if not is_int(size):
        return jsonify({"error message": "invalid size {}".format(size)}), 400
    if not is_int(offset):
        return jsonify({"error message": "invalid offset {}".format(offset)}), 400

    # normalise query parameters
    user_id = ObjectId(user_id)
    size = int(size)
    # cap number of posts to return
    size = 100 if size > 100 else size
    offset = int(offset)

    # query for user's posts (making sure to exclude the actual content)
    results = Post.objects(author=user_id) \
                  .exclude("content") \
                  .order_by("-created") \
                  .skip(offset) \
                  .limit(size)

    # serialize the posts
    user_posts = []
    for result in results:
        user_posts.append(result.serialize())

    return jsonify(user_posts)
