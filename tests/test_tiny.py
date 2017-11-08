from datetime import datetime
import unittest

from tiny import create_app
from tiny.models import Comment, Post, User

class TinyTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test").test_client()

    def tearDown(self):
        # clear the database
        Comment.objects.delete()
        Post.objects.delete()
        User.objects.delete()
        # sign user out
        self.sign_out()

    """
    Test helpers.
    """

    def register(self, data=None):
        if not data:
            data = self.get_mock_registration_form()
        return self.app.post("/user/register", data=data)

    def get_mock_registration_form(self):
        return dict(email="johndoe@example.com",
                    display_name="John Doe",
                    password="dbpassword",
                    confirmation="dbpassword")

    def sign_in(self, data=None):
        if not data:
            data = self.get_mock_sign_in_form()
        return self.app.post("/user/sign-in", data=data)

    def get_mock_sign_in_form(self):
        return dict(email="johndoe@example.com",
                    password="dbpassword")

    def sign_out(self):
        return self.app.get("/user/sign-out")

    def profile(self):
        return self.app.get("/user/profile")

    def profile_delete(self):
        return self.app.get("/user/profile/delete")

    def profile_update(self, data=None):
        if not data:
            data = self.get_mock_profile_update_form()
        return self.app.post("/user/profile", data=data)

    def get_mock_profile_update_form(self):
        return dict(display_name="John Smith",
                    avatar_url="http://www.example.com/avatar.jpg")

    """
    Registration tests.
    """

    def test_register_success(self):
        response = self.register()
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
        self.register()
        response = self.register()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    """
    Sign in tests.
    """

    def test_sign_in_success(self):
        self.register()
        response = self.sign_in()
        self.assertEqual(response.status_code, 302)

    def test_sign_in_invalid_email(self):
        self.register()
        form = self.get_mock_sign_in_form()
        form["email"] = "invalid"
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_no_email(self):
        self.register()
        form = self.get_mock_sign_in_form()
        del form["email"]
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_no_account_for_email(self):
        self.register()
        form = self.get_mock_sign_in_form()
        form["email"] = "another@example.com"
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 200)

    """
    Profile tests.
    """

    def test_profile_success(self):
        self.register()
        self.sign_in()
        response = self.profile()
        self.assertEqual(response.status_code, 200)

    def test_profile_sign_in_required(self):
        self.register()
        self.sign_out()
        response = self.profile()
        self.assertEqual(response.status_code, 302)

    def test_profile_delete_success(self):
        self.register()
        self.sign_in()
        response = self.profile_delete()
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

    def test_profile_delete_sign_in_required(self):
        self.register()
        self.sign_out()
        response = self.profile_delete()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_profile_update_success(self):
        self.register()
        self.sign_in()
        response = self.profile_update()
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Smith")
        self.assertEqual(user.avatar_url, "http://www.example.com/avatar.jpg")
        self.assertEqual(response.status_code, 200)

    def test_profile_update_display_name_too_long(self):
        self.register()
        self.sign_in()
        form = self.get_mock_profile_update_form()
        form["display_name"] = "123456789012345678901"
        response = self.profile_update(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_no_display_name(self):
        self.register()
        self.sign_in()
        form = self.get_mock_profile_update_form()
        del form["display_name"]
        response = self.profile_update(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_invalid_avatar_url(self):
        self.register()
        self.sign_in()
        form = self.get_mock_profile_update_form()
        form["avatar_url"] = "123456789012345678901"
        response = self.profile_update(data=form)
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_sign_in_required(self):
        self.register()
        self.sign_out()
        response = self.profile_update()
        user = User.objects.first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertIsNone(user.avatar_url)
        self.assertEqual(response.status_code, 302)

class HomeTest(TinyTest):
    def test_index(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

class UserTest(TinyTest):
    pass

class PostTest(TinyTest):
    pass

class CommentTest(TinyTest):
    pass

class SearchTest(TinyTest):
    pass

if __name__ == "__main__":
    unittest.main()
