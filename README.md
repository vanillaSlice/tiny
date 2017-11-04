# Tiny
A small blog app built with Flask.

## Environment
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
Create a file `instance/config.py`. Add the following properties:
* DEBUG - whether to print out debugging information
* SECRET_KEY - the app's secret key
* MONGODB_DB - the database name
* MONGODB_HOST - the host running a MongoDB instance
* MONGODB_PORT - the port of the MongoDB instance
* MONGODB_USERNAME - username
* MONGODB_PASSWORD - password

## Running Locally
```
python run.py
```
Then point your browser to [localhost:5000](http://localhost:5000).

## Testing
```
python -W ignore::DeprecationWarning -m unittest
```
