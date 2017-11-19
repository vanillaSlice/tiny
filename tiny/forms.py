"""
Exports forms used in Tiny app.
"""

from passlib.hash import sha256_crypt
from wtforms import Form, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL

from .helpers import get_user

class SignUpForm(Form):
    email = StringField("Email", validators=[
        DataRequired("Email is required."),
        Email()
    ])

    display_name = StringField("Display Name", validators=[
        DataRequired("Display Name is required."),
        Length(min=1, max=20, message="Display Name must be between 1 and 20 characters long.")
    ], render_kw={"maxlength": "20"})

    password = PasswordField("Password", validators=[
        DataRequired("Password is required."),
        Length(min=6, max=20, message="Password must be between 6 and 20 characters long."),
        EqualTo("confirmation", message="Passwords must match")
    ], render_kw={"maxlength": "20"})

    confirmation = PasswordField("Confirmation", validators=[
        DataRequired("Confirmation is required."),
        EqualTo("password", message="Passwords must match")
    ], render_kw={"maxlength": "20"})

    def validate(self):
        if not Form.validate(self):
            return False

        if get_user(email=self.email.data):
            self.email.errors.append("There is already an account with this email.")
            return False

        return True

class SignInForm(Form):
    email = StringField("Email", validators=[
        DataRequired("Email is required."),
        Email()
    ])

    password = PasswordField("Password", validators=[
        DataRequired("Password is required.")
    ], render_kw={"maxlength": "20"})

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = get_user(email=self.email.data)

        if not user:
            self.email.errors.append("There is no account with this email.")
            return False

        if not sha256_crypt.verify(self.password.data, user.password):
            self.password.errors.append("Incorrect password.")
            return False

        self.user = user

        return True

class UpdateProfileForm(Form):
    display_name = StringField("Display Name", validators=[
        DataRequired("Display Name is required."),
        Length(min=1, max=20, message="Display Name must be between 1 and 20 characters long.")
    ], render_kw={"maxlength": "20"})

    avatar_url = StringField("Avatar URL", validators=[
        DataRequired("Avatar URL is required."),
        URL(require_tld=False)
    ])

    bio = TextAreaField("Bio", validators=[
        Length(max=160, message="Bio cannot be longer than 160 characters.")
    ], render_kw={"maxlength": "160"})

class UpdatePasswordForm(Form):
    current_password = PasswordField("Current Password", validators=[
        DataRequired("Current Password is required."),
        Length(min=6, max=20, message="Current Password must be between 6 and 20 characters long.")
    ], render_kw={"maxlength": "20"})

    new_password = PasswordField("New Password", validators=[
        DataRequired("New Password is required."),
        EqualTo("confirmation", message="Passwords must match"),
        Length(min=6, max=20, message="New Password must be between 6 and 20 characters long.")
    ], render_kw={"maxlength": "20"})

    confirmation = PasswordField("Confirmation", validators=[
        DataRequired("Confirmation is required."),
        EqualTo("new_password", message="Passwords must match")
    ], render_kw={"maxlength": "20"})

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = kwargs["user"]

    def validate(self):
        if not Form.validate(self):
            return False

        if not sha256_crypt.verify(self.current_password.data, self.user.password):
            self.current_password.errors.append("Incorrect password.")
            return False

        return True

class PostForm(Form):
    title = StringField("Title", validators=[
        DataRequired("Title is required."),
        Length(min=1, max=100, message="Title must be between 1 and 100 characters long.")
    ], render_kw={"maxlength": "100"})

    preview = TextAreaField("Preview", validators=[
        Length(max=100, message="Preview cannot be longer than 100 characters.")
    ], render_kw={"maxlength": "100"})

    image_url = StringField("Image URL", validators=[
        DataRequired("Image URL is required."),
        URL(require_tld=False)
    ])

    content = TextAreaField("Content", validators=[
        DataRequired("Content is required."),
        Length(min=1, max=10_000, message="Content must be between 1 and 10,000 characters long.")
    ], render_kw={"maxlength": "10000"})

class CommentForm(Form):
    text = TextAreaField("Text", validators=[
        DataRequired("Text is required."),
        Length(min=1, max=320, message="Comment must be between 1 and 320 characters long.")
    ], render_kw={"maxlength": "320"})
