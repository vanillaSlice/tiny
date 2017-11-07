"""
Initialises Tiny app and brings together all of the various components.
"""

import os

from flask import Flask, render_template
from mongoengine import connect

def create_app(config="config.Default"):
    # create Flask app instance
    app = Flask(__name__, instance_relative_config=True)

    # load config from parameter (using the default config if not present)
    app.config.from_object(config)

    # not testing so load in other config properties
    if not app.config["TESTING"]:
        # override with instance config (if present)
        app.config.from_pyfile("config.py", silent=True)

        # load environment variables
        app.config.update(dict(
            DEBUG=os.environ.get("DEBUG", str(app.config["DEBUG"])).lower() == "true",
            SECRET_KEY=os.environ.get("SECRET_KEY", app.config["SECRET_KEY"]),
            MONGODB_URI=os.environ.get("MONGODB_URI", app.config["MONGODB_URI"])
        ))

    # connect to database
    connect(host=app.config["MONGODB_URI"])[__name__]

    # register blueprints
    from .views.home import home
    from .views.user import user
    from .views.post import post
    from .views.search import search
    app.register_blueprint(home)
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(search)

    # disable caching when debugging
    if app.debug:
        @app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response

    # attach 404 error handler
    @app.errorhandler(404)
    def handle_404(error):
        return render_template("404.html"), 404

    return app
