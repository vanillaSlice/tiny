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
                    password=sha256_crypt.hash("password"),
                    avatar_url="www.example.com/avatar.jpg",
                    joined=datetime.now())

    def get_mock_post(self, user):
        return Post(author=user,
                    title="Post title",
                    introduction="Post introduction",
                    image_url="http://www.example.com/image.png",
                    content="Post content",
                    published=datetime.now())

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

    def sign_up(self, data):
        return self.app.post("/user/sign-up", data=data)

    def get_mock_sign_up_form(self):
        return dict(email="johndoe@example.com",
                    display_name="John Doe",
                    password="password",
                    confirmation="password")

    def get_mock_sign_in_form(self):
        return dict(email="johndoe@example.com",
                    password="password")

    def update_profile(self, data):
        return self.app.post("/user/update-profile", data=data)

    def get_mock_update_profile_form(self):
        return dict(display_name="John Smith",
                    avatar_url="www.example.com/updated-avatar.jpg")

    def update_password(self, data):
        return self.app.post("/user/update-password", data=data)

    def get_mock_update_password_form(self):
        return dict(current_password="password",
                    new_password="newpassword",
                    confirmation="newpassword")

    """
    Sign up tests.
    """

    def test_sign_up_already_signed_in(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.get("/user/sign-up")
        self.assertEqual(response.status_code, 302)

    def test_sign_up_GET(self):
        response = self.app.get("/user/sign-up")
        self.assertEqual(response.status_code, 200)

    def test_sign_up_invalid_email(self):
        form = self.get_mock_sign_up_form()
        form["email"] = "invalid"
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_no_email(self):
        form = self.get_mock_sign_up_form()
        del form["email"]
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_display_name_too_long(self):
        form = self.get_mock_sign_up_form()
        form["display_name"] = "123456789012345678901"
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_no_display_name(self):
        form = self.get_mock_sign_up_form()
        del form["display_name"]
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_password_too_short(self):
        form = self.get_mock_sign_up_form()
        form["password"] = "12345"
        form["confirmation"] = "12345"
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_password_too_long(self):
        form = self.get_mock_sign_up_form()
        form["password"] = "123456789012345678901"
        form["confirmation"] = "123456789012345678901"
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_no_password(self):
        form = self.get_mock_sign_up_form()
        del form["password"]
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_no_confirmation(self):
        form = self.get_mock_sign_up_form()
        del form["confirmation"]
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_password_and_confirmation_dont_match(self):
        form = self.get_mock_sign_up_form()
        form["confirmation"] = "12345"
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_account_already_exists(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_up_form()
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_success(self):
        form = self.get_mock_sign_up_form()
        response = self.sign_up(data=form)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    """
    Sign in tests.
    """

    def test_sign_in_already_signed_in(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.get("/user/sign-in")
        self.assertEqual(response.status_code, 302)

    def test_sign_in_GET(self):
        response = self.app.get("/user/sign-in")
        self.assertEqual(response.status_code, 200)

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

    def test_sign_in_success(self):
        self.get_mock_user().save()
        form = self.get_mock_sign_in_form()
        response = self.sign_in(data=form)
        self.assertEqual(response.status_code, 302)

    """
    Sign out tests.
    """

    def test_sign_out_POST(self):
        response = self.app.post("/user/sign-out")
        self.assertEqual(response.status_code, 200)

    def test_sign_out_GET(self):
        response = self.app.get("/user/sign-out")
        self.assertEqual(response.status_code, 200)

    """
    Delete tests.
    """

    def test_delete_sign_in_required(self):
        self.get_mock_user().save()
        response = self.app.post("/user/delete")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_delete_GET(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.get("/user/delete")
        self.assertEqual(response.status_code, 200)

    def test_delete_success(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.post("/user/delete")
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

    """
    Settings tests.
    """

    def test_settings_sign_in_required(self):
        self.get_mock_user().save()
        response = self.app.get("/user/settings")
        self.assertEqual(response.status_code, 302)

    def test_settings_GET(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.get("/user/settings")
        self.assertEqual(response.status_code, 200)

    """
    Update profile tests.
    """

    def test_update_profile_sign_in_required(self):
        self.get_mock_user().save()
        response = self.app.get("/user/update-profile")
        self.assertEqual(response.status_code, 302)

    def test_update_profile_GET(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.get("/user/update-profile")
        self.assertEqual(response.status_code, 200)

    def test_update_profile_display_name_too_long(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_profile_form()
        form["display_name"] = "123456789012345678901"
        response = self.update_profile(data=form)
        user = User.objects(email="johndoe@example.com").first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertEqual(user.avatar_url, "www.example.com/avatar.jpg")
        self.assertEqual(response.status_code, 200)

    def test_update_profile_no_display_name(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_profile_form()
        del form["display_name"]
        response = self.update_profile(data=form)
        user = User.objects(email="johndoe@example.com").first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertEqual(user.avatar_url, "www.example.com/avatar.jpg")
        self.assertEqual(response.status_code, 200)

    def test_update_profile_no_avatar_url(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_profile_form()
        del form["avatar_url"]
        response = self.update_profile(data=form)
        user = User.objects(email="johndoe@example.com").first()
        self.assertEqual(user.display_name, "John Doe")
        self.assertEqual(user.avatar_url, "www.example.com/avatar.jpg")
        self.assertEqual(response.status_code, 200)

    def test_update_profile_success(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_profile_form()
        response = self.update_profile(data=form)
        user = User.objects(email="johndoe@example.com").first()
        self.assertEqual(user.display_name, "John Smith")
        self.assertEqual(user.avatar_url, "www.example.com/updated-avatar.jpg")
        self.assertEqual(response.status_code, 302)

    """
    Update password tests.
    """

    def test_update_password_sign_in_required(self):
        self.get_mock_user().save()
        response = self.app.get("/user/update-password")
        self.assertEqual(response.status_code, 302)

    def test_update_password_GET(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        response = self.app.get("/user/update-password")
        self.assertEqual(response.status_code, 200)

    def test_update_password_no_current_password(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        del form["current_password"]
        response = self.update_password(data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_new_password_too_short(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        form["new_password"] = "12345"
        form["confirmation"] = "12345"
        response = self.update_password(data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_new_password_too_long(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        form["new_password"] = "123456789012345678901"
        form["confirmation"] = "123456789012345678901"
        response = self.update_password(data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_no_new_password(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        del form["current_password"]
        response = self.update_password(data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_no_confirmation(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        del form["confirmation"]
        response = self.update_password(data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_new_password_and_confirmation_dont_match(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        del form["confirmation"]
        response = self.update_password(data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_success(self):
        self.get_mock_user().save()
        self.sign_in(dict(email="johndoe@example.com", password="password"))
        form = self.get_mock_update_password_form()
        response = self.update_password(data=form)
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

    """
    Posts tests.
    """

    def test_posts_invalid_author_id(self):
        response = self.app.get("/user/posts/invalid")
        self.assertEqual(response.data, b'{\n  "error message": "invalid author id invalid"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_posts_invalid_size(self):
        user = self.get_mock_user().save()
        response = self.app.get("/user/posts/{}?size=invalid".format(str(user.id)))
        self.assertEqual(response.data, b'{\n  "error message": "invalid size invalid"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_posts_invalid_offset(self):
        user = self.get_mock_user().save()
        response = self.app.get("/user/posts/{}?offset=invalid".format(str(user.id)))
        self.assertEqual(response.data, b'{\n  "error message": "invalid offset invalid"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_posts_success(self):
        user = self.get_mock_user().save()
        for i in range(10):
            self.get_mock_post(user).save()
        response = self.app.get("/user/posts/{}".format(str(user.id)))
        self.assertEqual(response.status_code, 200)

class PostTest(TestCase):
    pass

class CommentTest(TestCase):
    pass

class SearchTest(TestCase):
    pass
