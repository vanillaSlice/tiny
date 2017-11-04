import os
from flask import Flask
from mongoengine import connect

# create app instance
APP = Flask(__name__, instance_relative_config=True)

# load default config
APP.config.from_object("config")

# load instance config from environment variable or instance config if not set
APP.config.from_pyfile(os.environ.get("TINY_SETTINGS") or "config.py", silent=True)

# connect to database (authenticating if necessary)
if APP.config["MONGODB_USERNAME"] or APP.config["MONGODB_PASSWORD"]:
    CONNECTION = connect(APP.config["MONGODB_DB"],
                         host=APP.config["MONGODB_HOST"],
                         port=APP.config["MONGODB_PORT"],
                         username=APP.config["MONGODB_USERNAME"],
                         password=APP.config["MONGODB_PASSWORD"])
else:
    CONNECTION = connect(APP.config["MONGODB_DB"],
                         host=APP.config["MONGODB_HOST"],
                         port=APP.config["MONGODB_PORT"])

DB = CONNECTION[APP.config["MONGODB_DB"]]

from tiny import views
