# Tiny

[![Latest Release](https://img.shields.io/github/release/vanillaSlice/tiny.svg)](https://github.com/vanillaSlice/tiny/releases/latest)
[![Build Status](https://img.shields.io/travis/vanillaSlice/tiny/master.svg)](https://travis-ci.org/vanillaSlice/tiny)
[![Coverage Status](https://img.shields.io/coveralls/github/vanillaSlice/tiny/master.svg)](https://coveralls.io/github/vanillaSlice/tiny?branch=master)
[![License](https://img.shields.io/github/license/vanillaSlice/tiny.svg)](LICENSE)

A small blog app built with [Flask](http://flask.pocoo.org/) and [MongoDB](https://www.mongodb.com/). A deployed version can be viewed [here](https://slicetiny.herokuapp.com/). **If you set up an account, please use a dummy email address and password.**

## Getting Started
Install [virtualenv](https://virtualenv.pypa.io/en/stable/#) to create an isolated environment by running:
```
sudo pip install virtualenv
```

Create a new virtual environment:
```
virtualenv venv
```

Activate the virtual environment:
```
. venv/bin/activate
```

Install app dependencies:
```
pip install -r requirements.txt
```

If you install any additional dependencies in the virtual environment, you should probably save them using:
```
pip freeze > requirements.txt
```

To deactivate the virtual environment when finished:
```
deactivate
```

## Configuration
The following properties can be configured:

* DEBUG - (default is `True`)
* SECRET_KEY - (default is `default secret key`)
* SERVER_NAME - (default is `localhost:5000`)
* MONGODB_DB - (default is `tiny`)
* MONGODB_HOST - (default is `localhost`)
* MONGODB_PORT - (default is `27017`)
* MONGODB_USERNAME - (default is empty)
* MONGODB_PASSWORD - (default is empty)

URI style connections are also supported, just supply the URI as `MONGODB_HOST` (note that URI properties will take precedence).

To change these properties you can export them as environment variables or create a file `instance/config.py` (note that any environment variables take precedence).

## Running Locally
```
python run.py
```
Then point your browser to [localhost:5000](http://localhost:5000).

## Testing
```
python -m unittest
```

You may get deprecation warnings because [mongoengine](http://mongoengine.org/) uses deprecated methods under the hood. You can hide these by running:

```
python -W ignore::DeprecationWarning -m unittest
```
