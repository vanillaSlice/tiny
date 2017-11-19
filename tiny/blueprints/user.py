"""
Exports user routes.
"""

from flask import (Blueprint,
                   flash,
                   jsonify,
                   redirect,
                   render_template,
                   request,
                   session,
                   url_for)
from passlib.hash import sha256_crypt

from tiny.forms import SignInForm, SignUpForm, UpdatePasswordForm, UpdateProfileForm
from tiny.helpers import (get_posts,
                          serialize,
                          sign_in_required,
                          sign_out_required,
                          user_required)
from tiny.models import User

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/sign-up", methods=["GET", "POST"])
@sign_out_required
def sign_up():
    # parse the form
    form = SignUpForm(request.form)

    # render sign up form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("user/sign_up.html", form=form)

    # save new user
    new_user = User(email=form.email.data,
                    password=sha256_crypt.hash(form.password.data),
                    display_name=form.display_name.data).save()

    # make sure we store user id and avatar url in session
    session["user_id"] = str(new_user.id)
    session["avatar_url"] = new_user.avatar_url

    # notify user
    flash("Profile successfully created", "success")

    # redirect to user's profile page
    return redirect(url_for("user.show", user_id=session["user_id"]))

@user.route("/sign-in", methods=["GET", "POST"])
@sign_out_required
def sign_in():
    # parse the form
    form = SignInForm(request.form)

    # render sign in form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("user/sign_in.html", form=form)

    # make sure we store user id and avatar url in session
    session["user_id"] = str(form.user.id)
    session["avatar_url"] = form.user.avatar_url

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
@user_required
def show(user_id, selected_user):
    return render_template("user/show.html", user=selected_user)

@user.route("/settings", methods=["GET"])
@sign_in_required
def settings(current_user):
    return render_template("user/settings.html")

@user.route("/update-profile", methods=["GET", "POST"])
@sign_in_required
def update_profile(current_user):
    # parse the form
    form = UpdateProfileForm(request.form, current_user)

    # render update profile form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
        return render_template("user/update_profile.html", form=form)

    # update the user information
    form.populate_obj(current_user)
    current_user.save()

    # make sure we store the avatar url in session
    session["avatar_url"] = current_user.avatar_url

    # notify the user
    flash("Profile successfully updated", "success")

    # redirect back to settings page
    return redirect(url_for("user.settings"))

@user.route("/update-password", methods=["GET", "POST"])
@sign_in_required
def update_password(current_user):
    # parse the form
    form = UpdatePasswordForm(request.form, user=current_user)

    # render update password form if GET request or submitted form is invalid
    if request.method == "GET" or not form.validate():
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
def delete(current_user):
    # render delete page if GET request
    if request.method == "GET":
        return render_template("user/delete.html")

    current_user.delete()

    # make sure we clear the session
    session.clear()

    # notify user
    flash("Successfully deleted account", "success")

    # redirect back to homepage
    return redirect(url_for("home.index"))

@user.route("/<user_id>/posts", methods=["GET"])
@user_required
def posts(user_id, selected_user):
    # get query parameters
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 12, type=int)

    # query for user's posts (making sure to exclude the actual content)
    results = get_posts(user_id=user_id,
                        exclude=["content"],
                        order_by=["-created"],
                        skip=skip,
                        limit=limit)

    return jsonify(serialize(results))
