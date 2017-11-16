"""
Exports forms used in Tiny app.
"""

from wtforms import Form, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SignUpForm(Form):
    email = StringField(validators=[
        DataRequired(),
        Email()
    ])
    display_name = StringField(validators=[
        DataRequired(),
        Length(min=1, max=20)
    ], render_kw={"maxlength": "20"})
    password = PasswordField(validators=[
        DataRequired(),
        EqualTo("confirmation", message="Passwords must match"),
        Length(min=6, max=20)
    ], render_kw={"maxlength": "20"})
    confirmation = PasswordField(validators=[
        DataRequired()
    ])

class SignInForm(Form):
    email = StringField(validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField(validators=[
        DataRequired()
    ])

class UpdateProfileForm(Form):
    display_name = StringField(validators=[
        DataRequired(),
        Length(min=1, max=20)
    ], render_kw={"maxlength": "20"})
    avatar_url = StringField()
    bio = TextAreaField(validators=[
        Length(max=160)
    ], render_kw={"maxlength": "160"})

class UpdatePasswordForm(Form):
    current_password = PasswordField(validators=[
        DataRequired(),
    ])
    new_password = PasswordField(validators=[
        DataRequired(),
        EqualTo("confirmation", message="Passwords must match"),
        Length(min=6, max=20)
    ], render_kw={"maxlength": "20"})
    confirmation = PasswordField(validators=[
        DataRequired()
    ])

class PostForm(Form):
    title = StringField(validators=[
        DataRequired(),
        Length(min=1, max=100)
    ], render_kw={"maxlength": "100"})
    preview = TextAreaField(validators=[
        Length(max=100)
    ], render_kw={"maxlength": "100"})
    image_url = StringField()
    content = TextAreaField(validators=[
        DataRequired(),
        Length(min=1, max=10_000)
    ], render_kw={"maxlength": "10000"})

class CommentForm(Form):
    text = TextAreaField(validators=[
        DataRequired(),
        Length(min=1, max=320)
    ], render_kw={"maxlength": "320"})
