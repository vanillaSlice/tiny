from functools import wraps
from flask import redirect, request, session, url_for
from .models import User
from bson.objectid import ObjectId
from bson.errors import InvalidId

def sign_in_required(func):
    """
    Decorate routes to require sign in.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Checks if user is signed in, if not redirect to sign in page.
        """
        if session.get("email") is None:
            return redirect(url_for("sign_in", next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def get_current_user():
    return User.objects(email=session["email"]).first()

def get_user(_id):
    try:
        return User.objects(id=ObjectId(_id)).first()
    except InvalidId:
        return None
