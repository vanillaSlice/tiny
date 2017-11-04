from passlib.hash import sha256_crypt
from wtforms import Form, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from .models import User

class RegistrationForm(Form):
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
    confirmation = PasswordField("Confirm Password")

    def validate(self):
        if not Form.validate(self):
            return False

        if User.objects(email=self.email.data).first():
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

        if not user:
            self.email.errors.append("There is no account with this email")
            return False

        if not sha256_crypt.verify(self.password.data, user.password):
            self.password.errors.append("Incorrect password")
            return False

        # so we can access user data from view
        self.user = user

        return True
