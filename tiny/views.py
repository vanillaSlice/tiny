"""
Contains app routes.
"""

from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from tiny.helpers import login_required, is_valid_email, encrypt_password, verify_password
from tiny import app, db

"""
Disable caching when debugging.
"""
if app.debug:
    @app.after_request
    def after_request(response):
        """
        Ensures responses are not cached.
        """
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@app.route("/")
def index():
    """
    Renders home page.
    """
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registers a user"""

    ### VALIDATE EMAIL
    ### VALIDATE DISPLAY NAME
    ### VALIDATE PASSWORD

    # render register form if not a post request
    if request.method != 'POST':
        return render_template('register.html')

    # store references to form inputs
    email = request.form.get('email', None)
    display_name = request.form.get('display_name', None)
    password = request.form.get('password', None)
    confirmation = request.form.get('confirmation', None)

    # make sure email is provided
    if not email:
        return render_template('register.html', message="must provide email")

    # make sure email is valid
    if not is_valid_email(email):
        return render_template('register.html', message="Invalid email")

    # make sure display name is provided
    if not display_name:
        return render_template('register.html')

    # make sure password is provided
    if not password:
        return render_template('register.html',
                               message='must provide password')

    # make sure password is a valid length
    if len(password) < 6:
        return render_template('register.html',
                               message='password must be greater than 6 characters')

    # make sure password and confirmation are the same
    if password != confirmation:
        return render_template('register.html',
                               message='password and confirmation must be the same')

    # make sure the username is not already taken
    if db.users.find_one({'email': email}):
        return render_template('register.html',
                               message='user with email already exists')

    # add new user to database
    db.users.insert_one({
        'email': email,
        'display_name': display_name,
        'hash': encrypt_password(password),
        'joined': datetime.now()
    })

    session['email'] = email

    return redirect('/profile')

@app.route('/sign-in', methods=['GET', 'POST'])
def login():
    '''Allows user to login'''

    # render form if not a post request
    if request.method != 'POST':
        return render_template('login.html')

    # store references to form inputs
    email = request.form.get('email', None)
    password = request.form.get('password', None)

    # make sure username is provided
    if not email:
        return render_template('login.html',
                               message='must provider an email')

    # make sure password is provided
    if not password:
        return render_template('login.html',
                               message='must provide password')

    # get user from database
    user = db.users.find_one({'email': email})

    # make sure user exists
    if not user:
        return render_template('login.html',
                               message='user does not exist')

    # make sure password is correct
    if not verify_password(password, user['hash']):
        return render_template('login.html',
                               message='incorrect password')

    session['email'] = request.form['email']

    return redirect('/profile')

@app.route('/sign-out')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=db.users.find_one({'email': session['email']}))

'''POSTS'''

'''COMMENTS'''
