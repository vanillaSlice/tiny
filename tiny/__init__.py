import os
from flask import Flask
from mongoengine import connect

# create app instance
APP = Flask(__name__, instance_relative_config=True)

# # load default config
# APP.config.from_object("config")

# # load instance config from environment variable or instance config if not set
# APP.config.from_pyfile(os.environ.get("TINY_SETTINGS") or "config.py", silent=True)

APP.secret_key = os.environ.get("SECRET_KEY", "development key")
db_name = os.environ.get("MONGODB_DB", "tiny")
host = os.environ.get("MONGODB_HOST", "localhost")
port = os.environ.get("MONGODB_PORT", 27017)
username = os.environ.get("MONGODB_USERNAME", "")
password = os.environ.get("MONGODB_PASSWORD", "")

# connect to database (authenticating if necessary)
if username or password:
    CONNECTION = connect(db_name,
                         host=host,
                         port=port,
                         username=username,
                         password=password)
else:
    CONNECTION = connect(db_name,
                         host=host,
                         port=port)

DB = CONNECTION[db_name]

from tiny import views
