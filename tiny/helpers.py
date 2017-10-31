"""
Contains helper functions.
"""

import re
from functools import wraps
from flask import session, request, redirect, url_for
from passlib.hash import sha256_crypt

def login_required(func):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Checks if user is logged in, if not redirect to login page.
        """
        if session.get("email") is None:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def is_valid_email(email):
    """
    Returns if an email is valid or invalid.
    """
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None

def encrypt_password(password):
    """
    Encrypts a password.
    """
    return sha256_crypt.encrypt(password)

def verify_password(password, hashed_password):
    """
    Verifies a password against a hashed password.
    """
    return sha256_crypt.verify(password, hashed_password)
