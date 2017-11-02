"""
Initialises application and brings together all of the various components.
"""

from flask import Flask
from flask_mongoengine import MongoEngine

APP = Flask(__name__, instance_relative_config=True) # create app instance
APP.config.from_object("config") # load default config
APP.config.from_pyfile("config.py") # load instance config
MongoEngine(APP) # connect to database

from tiny import views
