# Tiny
A small blog app built with Flask. A deployed version can be viewed [here](https://enigmatic-spire-44057.herokuapp.com/).

## Development Environment
Install virtualenv to create an isolated environment:
```
sudo pip install virtualenv
```

Create virtual environment:
```
virtualenv venv
```

To activate the environment:
```
. venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

To save list of dependencies in virtual environment:
```
pip freeze > requirements.txt
```

To deactivate the environment:
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
python -W ignore::DeprecationWarning -m unittest
```
(Ignoring deprecation warnings because [mongoengine](http://mongoengine.org/) is using deprecated methods under the hood)
