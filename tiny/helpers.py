from functools import wraps

from flask import redirect, request, session, url_for
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .models import User

def sign_in_required(func):
    """
    Decorate routes to require sign in.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Checks if user is signed in, if not redirect to sign in page.
        """
        if session.get("id") is None:
            return redirect(url_for("user.sign_in", next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def is_signed_in():
    return session.get("id", None) != None

def get_current_user():
    return get_user_from_id(session.get("id", None))

def get_user_from_email(email):
    return User.objects(email=email).first()

def get_user_from_id(_id):
    try:
        return User.objects(id=ObjectId(_id)).first()
    except InvalidId:
        return None
