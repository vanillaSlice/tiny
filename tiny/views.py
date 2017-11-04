from datetime import datetime
from flask import redirect, render_template, request, session, url_for
from passlib.hash import sha256_crypt
from . import APP
from .forms import RegistrationForm, SignInForm
from .helpers import sign_in_required
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

@APP.route("/profile")
@sign_in_required
def profile():
    return render_template("profile.html", user=User.objects(email=session["email"]).first())
