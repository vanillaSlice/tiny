class Default(object):
    DEBUG = True
    SECRET_KEY = "default secret key"
    MONGODB_URI = "mongodb://localhost:27017/tiny"

class Test(Default):
    TESTING = True
    SECRET_KEY = "test secret key"
    MONGODB_URI = "mongomock://localhost:27017/tiny"
