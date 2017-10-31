"""
Initialises application and brings together all of the various components.
"""

from flask import Flask
from pymongo import MongoClient

def create_app():
    """
    Creates the flask app instance.
    """
    _app = Flask(__name__, instance_relative_config=True)
    _app.config.from_object("config") # default config
    _app.config.from_pyfile("config.py") # instance config
    return _app

def connect_db():
    """
    Connects to the database using config properties.
    """
    host = app.config["MONGODB_HOST"]
    port = app.config["MONGODB_PORT"]
    username = app.config["MONGODB_USERNAME"]
    password = app.config["MONGODB_PASSWORD"]
    name = app.config["MONGODB_NAME"]

    if username or password:
        mongo_client = MongoClient(host=host,
                                   port=port,
                                   username=username,
                                   password=password,
                                   connect=True)
    else:
        mongo_client = MongoClient(host=host, port=port, connect=True)

    return mongo_client[name]

app = create_app()
db = connect_db()

from tiny import views
