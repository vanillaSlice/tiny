from datetime import datetime
from flask import redirect, render_template, request, session, url_for
from passlib.hash import sha256_crypt
from . import APP
from .forms import RegistrationForm, SignInForm, UpdateProfileForm
from .helpers import get_current_user, get_user, sign_in_required
from .models import Comment, Post, User

# Disable caching when debugging
if APP.debug:
    @APP.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@APP.route("/")
def index():
    return render_template("index.html")

@APP.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        user = User(email=form.email.data,
                    display_name=form.display_name.data,
                    password=sha256_crypt.hash(form.password.data),
                    joined=datetime.now()).save()
        session["email"] = user.email
        return redirect(url_for("profile"))
    return render_template("register.html", form=form)

@APP.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    form = SignInForm(request.form)
    if request.method == "POST" and form.validate():
        session["email"] = form.user.email
        return redirect(request.args.get("next", None) or url_for("index"))
    return render_template("sign_in.html", form=form)

@APP.route("/sign-out")
def sign_out():
    session.pop("email", None)
    return redirect(url_for("index"))

@APP.route("/profile", methods=["GET", "POST"])
@sign_in_required
def profile():
    user = get_current_user()
    form = UpdateProfileForm(request.form)
    if request.method == "POST" and form.validate():
        user.display_name = form.display_name.data
        user.avatar_url = form.avatar_url.data
        user.save()
        return render_template("profile.html", user=user)
    return render_template("profile.html", form=form, user=user)

@APP.route("/profile/delete", methods=["GET"])
@sign_in_required
def profile_delete():
    user = get_current_user()
    if user:
        user.delete()
    return redirect(url_for("sign_out"))

@APP.route("/profile/<id>", methods=["GET"])
def profile_id(id):
    user = get_user(id)
    if not user:
        return redirect(url_for("index"))
    return render_template("profile.html", user=user)
