# Tiny

[![Latest Release](https://img.shields.io/github/release/vanillaSlice/tiny.svg)](https://github.com/vanillaSlice/tiny/releases/latest)
[![Build Status](https://img.shields.io/travis/vanillaSlice/tiny/master.svg)](https://travis-ci.org/vanillaSlice/tiny)
[![Coverage Status](https://img.shields.io/coveralls/github/vanillaSlice/tiny/master.svg)](https://coveralls.io/github/vanillaSlice/tiny?branch=master)
[![License](https://img.shields.io/github/license/vanillaSlice/tiny.svg)](LICENSE)

A small blog app built with [Flask](http://flask.pocoo.org/) and [MongoDB](https://www.mongodb.com/). 
A deployed version can be viewed [here](https://slicetiny.herokuapp.com/).
**If you set up an account, please use a dummy email address and password.**

## Screenshot

![Screenshot](/images/screenshot-1.png)

## Getting Started

* [With Docker](#with-docker)
* [Without Docker](#without-docker)

### With Docker

#### Prerequisites

* [Docker](https://www.docker.com/)

#### Running

From your terminal/command prompt run:

```
docker-compose up
```

Then point your browser to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### Without Docker

#### Installing Requirements

1. (Optional) Install [virtualenv](https://pypi.org/project/virtualenv/) and
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) and create a new environment.
2. Run `pip install -r requirements.txt`.

#### Setting up MongoDB

You can either:

* Install MongoDB locally by going [here](https://www.mongodb.com/download-center#community).

or:

* Create a database in the cloud using [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

#### Configuration

The following properties can be configured:

| Name                    | Purpose                                                          | Default              |
| ----------------------- | ---------------------------------------------------------------- | -------------------- |
| `DEBUG`                 | If debug mode is enabled.                                        | `False`              |
| `ENV`                   | Environment the app is running in.                               | `production`         |
| `MONGODB_DB`            | The MongoDB database name.                                       | `tiny`               |
| `MONGODB_HOST`          | The MongoDB host name.                                           | `127.0.0.1`          |
| `MONGODB_PASSWORD`      | The MongoDB password.                                            | `None`               |
| `MONGODB_PORT`          | The MongoDB port.                                                | `27017`              |
| `MONGODB_USERNAME`      | The MongoDB username.                                            | `None`               |
| `SECRET_KEY`            | A secret key used for security.                                  | `default secret key` |
| `SERVER_NAME`           | The host and port of the server.                                 | `127.0.0.1:5000`     |
| `SESSION_COOKIE_DOMAIN` | The domain match rule that the session cookie will be valid for. | `127.0.0.1:5000`     |
| `WTF_CSRF_ENABLED`      | If CSRF protection is enabled.                                   | `True`               |

To change these properties you can export them as environment variables or create a file `instance/config.py` (note
that any environment variables take precedence).

URI style connections are also supported for connecting to MongoDB, just supply the URI as `MONGODB_HOST` (note that
URI properties will take precedence).

#### Running

From your terminal/command prompt run:

```
./run.py
```

Then point your browser to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Technology Used

For those of you that are interested, the technology used in this project includes:

* [Python 3.7](https://www.python.org/downloads/release/python-372/)
* [Flask](http://flask.pocoo.org/) (Microframework)
* [MongoDB](https://www.mongodb.com/) and
[Flask-MongoEngine](http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/) (Database)
* [pytest](https://docs.pytest.org/en/latest/) and [Mongomock](https://github.com/mongomock/mongomock) (Testing)
* [Docker](https://www.docker.com/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
