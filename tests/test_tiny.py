from datetime import datetime
import unittest

from passlib.hash import sha256_crypt

from tiny import create_app
from tiny.models import Comment, Post, User

class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test").test_client()

    def tearDown(self):
        # clear the database
        Comment.objects.delete()
        Post.objects.delete()
        User.objects.delete()
        # make sure we don't leave user signed in
        self.sign_out()

    """
    Test helpers.
    """

    def sign_in(self, data):
        return self.app.post("/user/sign-in", data=data)

    def sign_out(self):
        return self.app.post("/user/sign-out")

    def get_mock_user(self):
        return User(email="johndoe@example.com",
                    display_name="John Doe",
                    password=sha256_crypt.hash("dbpassword"),
                    joined=datetime.now())

class TinyTest(TestCase):
    def test_404(self):
        response = self.app.get("/this/page/does/not/exist")
        self.assertEqual(response.status_code, 404)

class HomeTest(TestCase):
    def test_index(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

class UserTest(TestCase):
    """
    User Test Helpers
    """

    def register(self, data):
        return self.app.post("/user/register", data=data)

    def edit(self, data):
        return self.app.post("/user/edit", data=data)

    def get_mock_registration_form(self):
        return dict(email="johndoe@example.com",
                    display_name="John Doe",
                    password="dbpassword",
                    confirmation="dbpassword")

    def get_mock_sign_in_form(self):
        return dict(email="johndoe@example.com",
                    password="dbpassword")

    def get_mock_edit_form(self):
        return dict(display_name="John Smith",
                    avatar_url="http://www.example.com/avatar.jpg")

    """
    Registration tests.
    """

    def test_register_already_signed_in(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        response = self.app.get("/user/register")
        self.assertEqual(response.status_code, 302)

    def test_register_success(self):
        form = self.get_mock_registration_form()
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_register_invalid_email(self):
        form = self.get_mock_registration_form()
        form["email"] = "invalid"
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_no_email(self):
        form = self.get_mock_registration_form()
        del form["email"]
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_display_name_too_long(self):
        form = self.get_mock_registration_form()
        form["display_name"] = "123456789012345678901"
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_no_display_name(self):
        form = self.get_mock_registration_form()
        del form["display_name"]
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_password_too_short(self):
        form = self.get_mock_registration_form()
        form["password"] = "12345"
        form["confirmation"] = "12345"
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_password_too_long(self):
        form = self.get_mock_registration_form()
        form["password"] = "123456789012345678901"
        form["confirmation"] = "123456789012345678901"
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_no_password(self):
        form = self.get_mock_registration_form()
        del form["password"]
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_password_and_confirmation_dont_match(self):
        form = self.get_mock_registration_form()
        form["confirmation"] = "12345"
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_register_account_already_exists(self):
        self.get_mock_user().save()
        form = self.get_mock_registration_form()
        response = self.register(data=form)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    """
    Sign in tests.
    """

    def test_sign_in_already_signed_in(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        response = self.app.get("/user/sign-in")
        self.assertEqual(response.status_code, 302)

    def test_sign_in_success(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 302)

    def test_sign_in_invalid_email(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        form["email"] = "invalid"
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_no_email(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        del form["email"]
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_no_password(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        del form["password"]
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_no_account_for_email(self):
        form = self.get_mock_sign_in_form()
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_incorrect_password(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        form["password"] = "incorrect"
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    """
    Sign out tests.
    """

    def test_sign_out_already_signed_out(self):
        response = self.app.get("/user/sign-out")
        self.assertEqual(response.status_code, 200)

    """
    Delete tests.
    """

    def test_delete_success(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        response = self.app.post("/user/delete")
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

    def test_delete_sign_in_required(self):
        self.get_mock_user().save()
        response = self.app.post("/user/delete")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    """
    Edit tests.
    """

    def test_edit_success(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        form = self.get_mock_edit_form()
        response = self.edit(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, form["display_name"])
        self.assertEqual(user.avatar_url, form["avatar_url"])
        self.assertEqual(response.status_code, 302)

    def test_edit_display_name_too_long(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        form = self.get_mock_edit_form()
        form["display_name"] = "123456789012345678901"
        response = self.edit(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_no_display_name(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        form = self.get_mock_edit_form()
        del form["display_name"]
        response = self.edit(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_invalid_avatar_url(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="dbpassword"))
        form = self.get_mock_edit_form()
        form["avatar_url"] = "123456789012345678901"
        response = self.edit(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_sign_in_required(self):
        self.get_mock_user().save()
        response = self.app.post("/user/edit")
        self.assertEqual(response.status_code, 302)

    """
    Show tests.
    """

    def test_show_no_id(self):
        response = self.app.get("/user/show")
        self.assertEqual(response.status_code, 302)

    def test_show_no_user_with_id(self):
        response = self.app.get("/user/show/123456789")
        self.assertEqual(response.status_code, 302)

    def test_show_success(self):
        user = self.get_mock_user().save()
        response = self.app.get("/user/show/{}".format(str(user.id)))
        self.assertEqual(response.status_code, 200)

class PostTest(TestCase):
    pass

class CommentTest(TestCase):
    pass

class SearchTest(TestCase):
    pass
