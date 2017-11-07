from flask import Blueprint, render_template

comment = Blueprint("comment", __name__, url_prefix="/comment")
