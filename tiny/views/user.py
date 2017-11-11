from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from passlib.hash import sha256_crypt

from tiny.forms import EditUserForm, SignInForm, SignUpForm
from tiny.helpers import (get_current_user,
                          get_user_from_id,
                          is_signed_in,
                          sign_in_required)
from tiny.models import User

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    # redirect to home page if already signed in
    if is_signed_in():
        return redirect(url_for("home.index"))

    form = SignUpForm(request.form)

    # register new user
    if request.method == "POST" and form.validate():
        new_user = User(email=form.email.data,
                        display_name=form.display_name.data,
                        password=sha256_crypt.hash(form.password.data),
                        joined=datetime.now()).save()

        # make sure we store user session
        session["id"] = str(new_user.id)
        session["avatar_url"] = url_for("static", filename="img/default-avatar.png")

        return redirect(url_for("user.show", id=session["id"]))

    # render registration form
    return render_template("user/sign_up.html", form=form)

@user.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    # redirect to home page if already signed in
    if is_signed_in():
        return redirect(url_for("home.index"))

    form = SignInForm(request.form)

    # sign user in
    if request.method == "POST" and form.validate():
        # make sure we store user session
        session["id"] = str(form.user.id)
        session["avatar_url"] = form.user.avatar_url or url_for("static", filename="img/default-avatar.png")

        return redirect(request.args.get("next", None) or url_for("home.index"))

    # render sign in form
    return render_template("user/sign_in.html", form=form)

@user.route("/sign-out", methods=["GET", "POST"])
def sign_out():
    # clear session i.e. sign user out
    if request.method == "POST":
        session.clear()

    # render sign out screen
    return render_template("user/sign_out.html")

@user.route("/delete", methods=["GET", "POST"])
@sign_in_required
def delete():
    # delete the user
    if request.method == "POST":
        get_current_user().delete()

        # make sure we clear the session
        session.clear()

        return redirect(url_for("home.index"))

    # render delete screen
    return render_template("user/delete.html")

@user.route("/edit", methods=["GET", "POST"])
@sign_in_required
def edit():
    form = EditUserForm(request.form)

    # edit the user
    if request.method == "POST" and form.validate():
        current_user = get_current_user()
        current_user.display_name = form.display_name.data
        current_user.avatar_url = form.avatar_url.data
        current_user.save()
        flash("Profile successfully updated", "success")
        return redirect(url_for("user.show"))

    # render edit form
    return render_template("user/edit.html", form=form)

@user.route("/settings", methods=["GET"])
@sign_in_required
def settings():
    return render_template("user/settings.html")

@user.route("/show", methods=["GET"], defaults={"user_id": None})
@user.route("/show/<user_id>", methods=["GET"])
def show(user_id):
    user = get_user_from_id(user_id)

    # couldn't find user - redirect to home page
    if user is None:
        flash("Oops - we couldn't find that profile", "danger")
        return redirect(url_for("home.index"))

    user['id'] = str(user['id'])

    return render_template("user/show.html", user=user)
