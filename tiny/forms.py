"""
Contains forms used in Tiny app.
"""

from bson.objectid import ObjectId
from flask import session
from passlib.hash import sha256_crypt
from wtforms import Form, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import User

class SignUpForm(Form):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])
    display_name = StringField("Display Name", validators=[
        DataRequired(),
        Length(max=20)
    ])
    password = PasswordField("Password", validators=[
        DataRequired(),
        EqualTo("confirmation", message="Passwords must match"),
        Length(min=6, max=20)
    ])
    confirmation = PasswordField("Confirm Password", validators=[
        DataRequired()
    ])

    def validate(self):
        if not Form.validate(self):
            return False

        # check if there is an existing account with this email
        if User.objects(email=self.email.data):
            self.email.errors.append("There is already an account with that email")
            return False

        return True

class SignInForm(Form):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField("Password", validators=[
        DataRequired()
    ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.objects(email=self.email.data).first()

        # check if there is an existing account with this email
        if not user:
            self.email.errors.append("There is no account with this email")
            return False

        # check password is correct
        if not sha256_crypt.verify(self.password.data, user.password):
            self.password.errors.append("Incorrect password")
            return False

        # so we can access user data from view
        self.user = user

        return True

class UpdateProfileForm(Form):
    display_name = StringField("Display Name", validators=[
        DataRequired(),
        Length(max=20)
    ])
    avatar_url = StringField("Avatar URL", validators=[
        DataRequired()
    ])

class UpdatePasswordForm(Form):
    current_password = PasswordField("Current Password", validators=[
        DataRequired(),
    ])
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        EqualTo("confirmation", message="Passwords must match"),
        Length(min=6, max=20)
    ])
    confirmation = PasswordField("Confirm Password", validators=[
        DataRequired()
    ])

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.objects(id=ObjectId(session.get("user_id"))).first()

        # check password is correct
        if not sha256_crypt.verify(self.current_password.data, user.password):
            self.current_password.errors.append("Incorrect password")
            return False

        return True

class NewPostForm(Form):
    title = StringField("Title")
    introduction = StringField("Introduction")
    image_url = StringField("Image URL")
    content = StringField("Content")
