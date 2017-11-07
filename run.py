"""
Creates an instance of Tiny app.

This app will be run locally if using 'python run.py'.
When deploying to Heroku, Gunicorn is used and does not
use the Flask development server.
"""

from tiny import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
