"""
Exports a function to create an instance of the Tiny app.
"""

import os

from flask import abort, Flask, render_template
from flask_assets import Environment
from flask_mongoengine import MongoEngine

from tiny.assets import bundles
from tiny.helpers import markdown_to_html

version = 'v1.4.1'

assets = Environment()

mongoengine = MongoEngine()

def create_app(testing=False):
    """
    Creates an instance of the Tiny app.
    """

    app = Flask(__name__, instance_relative_config=True)

    # load default config
    app.config.from_object('config.Default')

    # load instance config (if present)
    app.config.from_pyfile('config.py', silent=True)

    # load test config (if testing)
    if testing:
        app.config.from_object('config.Test')

    app.config.update({'TESTING': testing})

    # load environment variables (if present)
    app.config.update({
        'DEBUG': os.environ.get('DEBUG', str(app.config.get('DEBUG'))).lower() == 'true',
        'ENV': os.environ.get('ENV', app.config.get('ENV')),
        'MONGODB_DB': os.environ.get('MONGODB_DB', app.config.get('MONGODB_DB')),
        'MONGODB_HOST': os.environ.get('MONGODB_HOST', app.config.get('MONGODB_HOST')),
        'MONGODB_PASSWORD': os.environ.get('MONGODB_PASSWORD', app.config.get('MONGODB_PASSWORD')),
        'MONGODB_PORT': int(os.environ.get('MONGODB_PORT', app.config.get('MONGODB_PORT'))),
        'MONGODB_USERNAME': os.environ.get('MONGODB_USERNAME', app.config.get('MONGODB_USERNAME')),
        'SECRET_KEY': os.environ.get('SECRET_KEY', app.config.get('SECRET_KEY')),
        'SERVER_NAME': os.environ.get('SERVER_NAME', app.config.get('SERVER_NAME')),
        'SESSION_COOKIE_DOMAIN':
            os.environ.get('SESSION_COOKIE_DOMAIN', app.config.get('SESSION_COOKIE_DOMAIN')),
        'WTF_CSRF_ENABLED':
            os.environ.get('WTF_CSRF_ENABLED', str(app.config.get('WTF_CSRF_ENABLED'))).lower() == 'true'
    })

    # inject version
    @app.context_processor
    def inject_version():
        return {'version': version}

    # init extensions
    assets.init_app(app)
    mongoengine.init_app(app)

    # disable strict trailing slashes e.g. so /user/sign-in and /user/sign-in/ both resolve to same endpoint
    app.url_map.strict_slashes = False

    # register blueprints
    from tiny.blueprints.home import home
    from tiny.blueprints.post import post
    from tiny.blueprints.search import search
    from tiny.blueprints.user import user
    app.register_blueprint(home)
    app.register_blueprint(post)
    app.register_blueprint(search)
    app.register_blueprint(user)

    # register asset bundles
    assets.register(bundles)

    # register filters
    @app.template_filter('format_date')
    def format_date_filter(s):
        return s.strftime('%b %d %Y')

    @app.template_filter('markdown_to_html')
    def markdown_to_html_filter(s):
        return markdown_to_html(s)

    # attach catch all error handler
    @app.errorhandler(Exception)
    def handle_exception(_):
        abort(500)

    # attach 404 error handler
    @app.errorhandler(404)
    def handle_404(error):
        return render_template('404.html', error=error), 404

    # attach 500 error handler
    @app.errorhandler(500)
    def handle_500(error):
        return render_template('500.html', error=error), 500

    # disable caching when debugging
    if app.debug:
        @app.after_request
        def after_request(response):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Expires'] = 0
            response.headers['Pragma'] = 'no-cache'
            return response

    return app
