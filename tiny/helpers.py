"""
Exports reusable helper functions.
"""

from functools import wraps

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import redirect, request, session, url_for

def sign_in_required(func):
    """
    Decorate routes to require sign in.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Checks if user is signed in, if not redirect to sign in page.
        """
        if session.get("user_id") is None:
            return redirect(url_for("user.sign_in", next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def del_none(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d

def is_valid_object_id(value):
    try:
        ObjectId(value)
        return True
    except InvalidId:
        return False

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
