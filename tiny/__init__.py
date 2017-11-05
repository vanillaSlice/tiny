import os
from flask import Flask
from mongoengine import connect

def create_app(config=None):
    # create Flask app instance
    _app = Flask(__name__)

    # load default config
    _app.config.from_object("config.Default")

    # load environment variables
    _app.config.update(dict(
        DEBUG=os.environ.get("DEBUG", str(_app.config["DEBUG"])).lower() == "true",
        SECRET_KEY=os.environ.get("SECRET_KEY", _app.config["SECRET_KEY"]),
        MONGODB_URI=os.environ.get("MONGODB_URI", _app.config["MONGODB_URI"])
    ))

    # override with instance config
    _app.config.from_object(config)

    # connect to database
    connect(host=_app.config["MONGODB_URI"])[__name__]

    # register blueprints
    from .views import home, user
    _app.register_blueprint(home)
    _app.register_blueprint(user)

    # disable caching when debugging
    if _app.debug:
        @_app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response

    return _app
