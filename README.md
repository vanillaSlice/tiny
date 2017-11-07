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
Export the following environment variables to override the defaults:

* DEBUG - whether to print out debugging information
* SECRET_KEY - the app's secret key
* MONGODB_URI - the MongoDB instance URI

Default configuration properties can be viewed in [config.py](config.py).

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
