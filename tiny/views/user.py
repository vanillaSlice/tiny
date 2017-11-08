from datetime import datetime

from flask import Blueprint, redirect, render_template, request, session, url_for
from passlib.hash import sha256_crypt

from tiny.forms import RegistrationForm, SignInForm, UpdateProfileForm
from tiny.helpers import get_current_user, get_user, sign_in_required
from tiny.models import Comment, Post, User

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        _user = User(email=form.email.data,
                     display_name=form.display_name.data,
                     password=sha256_crypt.hash(form.password.data),
                     joined=datetime.now()).save()
        session["email"] = _user.email
        return redirect(url_for("user.profile"))
    return render_template("user/register.html", form=form)

@user.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    form = SignInForm(request.form)
    if request.method == "POST" and form.validate():
        session["email"] = form.user.email
        return redirect(request.args.get("next", None) or url_for("home.index"))
    return render_template("user/sign_in.html", form=form)

@user.route("/sign-out")
def sign_out():
    session.pop("email", None)
    return redirect(url_for("home.index"))

@user.route("/profile", methods=["GET", "POST"])
@sign_in_required
def profile():
    user = get_current_user()
    form = UpdateProfileForm(request.form)
    if request.method == "POST" and form.validate():
        user.display_name = form.display_name.data
        user.avatar_url = form.avatar_url.data
        user.save()
        return render_template("user/show.html", user=user)
    return render_template("user/show.html", form=form, user=user)

@user.route("/profile/delete", methods=["GET"])
@sign_in_required
def profile_delete():
    user = get_current_user()
    if user:
        user.delete()
    return redirect(url_for("user.sign_out"))

@user.route("/profile/<id>", methods=["GET"])
def profile_id(id):
    user = get_user(id)
    if not user:
        return redirect(url_for("home.index"))
    return render_template("user/show.html", user=user)
