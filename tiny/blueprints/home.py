"""
Exports home routes.
"""

from flask import Blueprint, render_template

home = Blueprint('home', __name__, url_prefix='/')

@home.route('/')
def index():
    """
    Index route.
    """

    return render_template('home/index.html')
