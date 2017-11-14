# Tiny
A small blog app built with [Flask](http://flask.pocoo.org/) and [MongoDB](https://www.mongodb.com/). A deployed version can be viewed [here](https://enigmatic-spire-44057.herokuapp.com/).

## Development Environment
Install [virtualenv](https://virtualenv.pypa.io/en/stable/#) to create an isolated environment:
```
sudo pip install virtualenv
```

Create virtual environment:
```
virtualenv venv
```

Activate the environment:
```
. venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

To save list of dependencies:
```
pip freeze > requirements.txt
```

To deactivate the environment when finished:
```
deactivate
```

## Configuration
The following properties can be configured:

* DEBUG - whether to print out debugging information
* SECRET_KEY - the app's secret key
* MONGODB_URI - the MongoDB instance URI

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
