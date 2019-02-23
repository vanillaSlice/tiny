"""
Exports forms used in Tiny app.
"""

from flask_wtf import FlaskForm
from passlib.hash import sha256_crypt
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL

from tiny.helpers import get_user

class SignUpForm(FlaskForm):
    """
    Sign up form.
    """

    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

    display_name = StringField('Display Name', validators=[
        DataRequired(),
        Length(min=1, max=50)
    ])

    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirmation', message='Password and Confirmation must match.')
    ])

    confirmation = PasswordField('Confirmation', validators=[
        DataRequired(),
        EqualTo('password', message='Password and Confirmation must match.')
    ])

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False

        if get_user(email=self.email.data):
            self.email.errors.append('There is already an account with this email.')
            return False

        return True

class SignInForm(FlaskForm):
    """
    Sign in form.
    """

    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField('Password', validators=[
        DataRequired()
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False

        user = get_user(email=self.email.data)

        if not user or not sha256_crypt.verify(self.password.data, user.password):
            self.email.errors.append('Incorrect email.')
            self.password.errors.append('Incorrect password.')
            return False

        self.user = user

        return True

class UpdateProfileForm(FlaskForm):
    """
    Update profile form.
    """

    display_name = StringField('Display Name', validators=[
        DataRequired(),
        Length(min=1, max=50)
    ])

    avatar_url = StringField('Avatar URL', validators=[
        DataRequired(),
        URL(require_tld=False)
    ])

    bio = TextAreaField('Bio', validators=[
        Length(max=160)
    ])

class UpdatePasswordForm(FlaskForm):
    """
    Update password form.
    """

    current_password = PasswordField('Current Password', validators=[
        DataRequired()
    ])

    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirmation', message='New Password and Confirmation must match.')
    ])

    confirmation = PasswordField('Confirmation', validators=[
        DataRequired(),
        EqualTo('new_password', message='New Password and Confirmation must match.')
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = kwargs['user']

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False

        if not sha256_crypt.verify(self.current_password.data, self.user.password):
            self.current_password.errors.append('Incorrect password.')
            return False

        return True

class PostForm(FlaskForm):
    """
    Post form.
    """

    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=160)
    ])

    lead_paragraph = TextAreaField('Lead Paragraph', validators=[
        Length(max=500)
    ])

    image_url = StringField('Image URL', validators=[
        DataRequired(),
        URL(require_tld=False)
    ])

    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=1, max=10_000)
    ])

class CommentForm(FlaskForm):
    """
    Comment form.
    """

    text = TextAreaField('Text', validators=[
        DataRequired('Comment text is required.'),
        Length(min=1, max=500, message='Comment must be between 1 and 500 characters long.')
    ])
