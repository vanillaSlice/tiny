"""
Exports a function to create an instance of Tiny app.
"""

import os

from flask import Flask, render_template
from flask_assets import Environment
from mongoengine import connect

from .assets import bundles

def create_app(config="config.Default"):
    # create the app instance
    app = Flask(__name__, instance_relative_config=True)

    # load config from parameter (using the default config if not present)
    app.config.from_object(config)

    # load instance config and environment variables if not testing
    if not app.config["TESTING"]:
        # load instance config (if present)
        app.config.from_pyfile("config.py", silent=True)

        # load environment variables (if present)
        app.config.update(dict(
            DEBUG=os.environ.get("DEBUG", str(app.config["DEBUG"])).lower() == "true",
            SECRET_KEY=os.environ.get("SECRET_KEY", app.config["SECRET_KEY"]),
            MONGODB_URI=os.environ.get("MONGODB_URI", app.config["MONGODB_URI"])
        ))

    # connect to database
    connect(host=app.config["MONGODB_URI"])[__name__]

    # disable strict trailing slashes i.e. so /user/sign-in and /user/sign-in/ both resolve
    app.url_map.strict_slashes = False

    # register blueprints
    from .blueprints.home import home
    from .blueprints.user import user
    from .blueprints.post import post
    from .blueprints.comment import comment
    from .blueprints.search import search
    app.register_blueprint(home)
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(comment)
    app.register_blueprint(search)

    # register asset bundles
    assets = Environment(app)
    assets.register(bundles)

    # attach 404 error handler
    @app.errorhandler(404)
    def handle_404(error):
        return render_template("404.html", error=error), 404

    # disable caching when debugging
    if app.debug:
        @app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response

    return app
