import os

from flask import Flask, render_template
from mongoengine import connect

def create_app(config=None):
    # create Flask app instance
    app = Flask(__name__)

    # load default config
    app.config.from_object("config.Default")

    # load environment variables
    app.config.update(dict(
        DEBUG=os.environ.get("DEBUG", str(app.config["DEBUG"])).lower() == "true",
        SECRET_KEY=os.environ.get("SECRET_KEY", app.config["SECRET_KEY"]),
        MONGODB_URI=os.environ.get("MONGODB_URI", app.config["MONGODB_URI"])
    ))

    # override with instance config (if provided)
    app.config.from_object(config)

    # connect to database
    connect(host=app.config["MONGODB_URI"])[__name__]

    # register blueprints
    from .views import home, user, post
    app.register_blueprint(home)
    app.register_blueprint(user)
    app.register_blueprint(post)

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
    def handle_404(e):
        return render_template("404.html"), 404

    return app
