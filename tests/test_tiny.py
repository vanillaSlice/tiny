import os
# make sure we use test configuration
os.environ["TINY_SETTINGS"] = "../tests/config.py"

from datetime import datetime
import unittest
from passlib.hash import sha256_crypt
import tiny
from tiny.models import Comment, Post, User

class TinyTest(unittest.TestCase):
    def setUp(self):
        self.app = tiny.APP.test_client()
        self.db = tiny.DB

    def tearDown(self):
        # clear the database
        Comment.objects.delete()
        Post.objects.delete()
        User.objects.delete()

    def get_mock_user(self):
        return User(email="johndoe@example.com",
                    display_name="John Doe",
                    password=sha256_crypt.hash("dbpassword"),
                    joined=datetime.now())

    def test_index(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    """
    Registration tests.
    """

    def get_mock_registration_form(self):
        return dict(email="johndoe@example.com",
                    display_name="John Doe",
                    password="dbpassword",
                    confirmation="dbpassword")

    def registration_assertions(self, form, expected_user_count, expected_status_code):
        response = self.app.post("/register", data=form)
        self.assertEqual(self.db.user.count(), expected_user_count)
        self.assertEqual(response.status_code, expected_status_code)

    def test_register_success(self):
        form = self.get_mock_registration_form()
        self.registration_assertions(form=form, expected_user_count=1, expected_status_code=302)

    def test_register_invalid_email(self):
        form = self.get_mock_registration_form()
        form["email"] = "invalid"
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_no_email(self):
        form = self.get_mock_registration_form()
        del form["email"]
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_display_name_too_long(self):
        form = self.get_mock_registration_form()
        form["display_name"] = "123456789012345678901"
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_no_display_name(self):
        form = self.get_mock_registration_form()
        del form["display_name"]
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_password_too_short(self):
        form = self.get_mock_registration_form()
        form["password"] = "12345"
        form["confirmation"] = "12345"
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_password_too_long(self):
        form = self.get_mock_registration_form()
        form["password"] = "123456789012345678901"
        form["confirmation"] = "123456789012345678901"
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_no_password(self):
        form = self.get_mock_registration_form()
        del form["password"]
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_password_and_confirmation_dont_match(self):
        form = self.get_mock_registration_form()
        form["confirmation"] = "12345"
        self.registration_assertions(form=form, expected_user_count=0, expected_status_code=200)

    def test_register_account_already_exists(self):
        self.get_mock_user().save()
        form = self.get_mock_registration_form()
        self.registration_assertions(form=form, expected_user_count=1, expected_status_code=200)

    """
    Sign in tests.
    """

    def get_mock_sign_in_form(self):
        return dict(email="johndoe@example.com",
                    password="dbpassword")

    def sign_in_assertions(self, form, expected_status_code):
        response = self.app.post("/sign-in", data=form)
        self.assertEqual(response.status_code, expected_status_code)

    def test_sign_in_success(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        self.sign_in_assertions(form=form, expected_status_code=302)

    def test_sign_in_invalid_email(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        form["email"] = "invalid"
        self.sign_in_assertions(form=form, expected_status_code=200)

    def test_sign_in_no_email(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        del form["email"]
        self.sign_in_assertions(form=form, expected_status_code=200)

    def test_sign_in_no_account_for_email(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        form["email"] = "another@example.com"
        self.sign_in_assertions(form=form, expected_status_code=200)

    """
    Profile tests.
    """

    """
    Post tests.
    """

    """
    Comment tests.
    """

if __name__ == '__main__':
    unittest.main()
