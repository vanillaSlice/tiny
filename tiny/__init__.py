"""
Exports a function to create an instance of Tiny app.
"""

import os

from flask import Flask, render_template
from flask_assets import Environment
from flask_mongoengine import MongoEngine

from .assets import bundles

def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)

    if testing:
        # load test config
        app.config.from_object("config.Test")
    else:
        # load default config
        app.config.from_object("config.Default")

        # load instance config (if present)
        app.config.from_pyfile("config.py", silent=True)

        # load environment variables (if present)
        app.config.update({
            "DEBUG": os.environ.get("DEBUG", str(app.config.get("DEBUG"))).lower() == "true",
            "SECRET_KEY": os.environ.get("SECRET_KEY", app.config.get("SECRET_KEY")),
            "SERVER_NAME": os.environ.get("SERVER_NAME", app.config.get("SERVER_NAME")),
            "MONGODB_DB": os.environ.get("MONGODB_DB", app.config.get("MONGODB_DB")),
            "MONGODB_HOST": os.environ.get("MONGODB_HOST", app.config.get("MONGODB_HOST")),
            "MONGODB_PORT": os.environ.get("MONGODB_PORT", app.config.get("MONGODB_PORT")),
            "MONGODB_USERNAME": os.environ.get("MONGODB_USERNAME", app.config.get("MONGODB_USERNAME")),
            "MONGODB_PASSWORD": os.environ.get("MONGODB_PASSWORD", app.config.get("MONGODB_PASSWORD"))
        })

    # connect to database
    MongoEngine(app)

    # disable strict trailing slashes i.e. so /user/sign-in and /user/sign-in/ both
    # resolve to same endpoint
    app.url_map.strict_slashes = False

    # register blueprints
    from .blueprints.home import home
    from .blueprints.user import user
    from .blueprints.post import post
    from .blueprints.search import search
    app.register_blueprint(home)
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(search)

    # register asset bundles
    assets = Environment(app)
    assets.register(bundles)

    # register filters
    @app.template_filter("format_date")
    def format_date_filter(s):
        return s.strftime('%b %d %Y')

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
