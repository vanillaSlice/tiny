import json
import random
import string
import unittest
from unittest import mock

from passlib.hash import sha256_crypt

from tiny import create_app
from tiny.models import Comment, Post, User

class TestCase(unittest.TestCase):
    def setUp(self):
        # set up test app instance
        self.app = create_app(testing=True)
        self.app.app_context().push()
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        # make sure we start with a clean database
        self.clear_db()

        # make sure we set up a user
        self.email = "me@example.com"
        self.password = "password"
        self.user = self.get_mock_user()
        self.user.email = self.email
        self.user.password = sha256_crypt.hash("password")
        self.user.save()

        # make sure we sign in
        self.sign_in({"email": self.email, "password": self.password})

    def tearDown(self):
        self.clear_db()
        self.sign_out()

    """
    Test helper functions.
    """

    def clear_db(self):
        Comment.objects.delete()
        Post.objects.delete()
        User.objects.delete()

    def sign_in(self, data):
        return self.client.post("/user/sign-in", data=data)

    def sign_out(self):
        return self.client.post("/user/sign-out")

    def random_string(self, size):
        return "".join(random.choice(string.ascii_lowercase) for i in range(size))

    def random_email(self):
        return "{}@{}.com".format(self.random_string(7), self.random_string(7))

    def random_url(self):
        return "http://www.{}.com".format(self.random_string(7))

    def get_mock_user(self):
        return User(email=self.random_email(),
                    password=self.random_string(10),
                    display_name=self.random_string(10),
                    bio=self.random_string(10),
                    avatar_url=self.random_url())

    def get_mock_post(self, author=None):
        if not author:
            author = self.get_mock_user().save()

        return Post(author=author,
                    title=self.random_string(10),
                    lead_paragraph=self.random_string(10),
                    image_url=self.random_url(),
                    content=self.random_string(10))

    def get_mock_comment(self, author=None, post=None):
        if not author:
            author = self.get_mock_user().save()
        if not post:
            post = self.get_mock_post().save()

        return Comment(author=author,
                       post=post,
                       text=self.random_string(10))

    def get_mock_sign_up_data(self):
        password = self.random_string(10)
        return {"email": self.random_email(),
                "display_name": self.random_string(10),
                "password": password,
                "confirmation": password}

    def get_mock_sign_in_data(self):
        return {"email": self.random_email(),
                "password": self.random_string(10)}

    def get_mock_update_profile_data(self):
        return {"display_name": self.random_string(10),
                "avatar_url": self.random_url(),
                "bio": self.random_string(10)}

    def get_mock_update_password_data(self):
        new_password = self.random_string(10)
        return {"current_password": self.random_string(10),
                "new_password": new_password,
                "confirmation": new_password}

    def get_mock_post_data(self):
        return {"title": self.random_string(10),
                "lead_paragraph": self.random_string(10),
                "image_url": self.random_url(),
                "content": self.random_string(10)}

    def get_mock_comment_data(self):
        return {"text": self.random_string(10)}

class TinyTest(TestCase):
    def test_404(self):
        response = self.client.get("/this/page/does/not/exist")
        self.assertEqual(response.status_code, 404)

class HomeTest(TestCase):
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class UserTest(TestCase):
    """
    Sign up tests.
    """

    def assert_sign_up_successful(self, data):
        response = self.client.post("/user/sign-up", data=data)
        user = User.objects(email=data["email"]).first()
        self.assertTrue(sha256_crypt.verify(data["password"], user.password))
        self.assertEqual(user.display_name, data["display_name"])
        self.assertIsNone(user.bio)
        self.assertTrue("/static/img/default-avatar.jpg" in user.avatar_url)
        self.assertIsNotNone(user.created)
        self.assertEqual(response.status_code, 302)

    def assert_sign_up_unsuccessful(self, data):
        response = self.client.post("/user/sign-up", data=data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_already_signed_in(self):
        response = self.client.get("/user/sign-up")
        self.assertEqual(response.status_code, 302)

    def test_sign_up_GET(self):
        self.sign_out()
        response = self.client.get("/user/sign-up")
        self.assertEqual(response.status_code, 200)

    def test_sign_up_no_email(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["email"] = ""
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_invalid_email(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["email"] = "invalid"
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_no_display_name(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["display_name"] = ""
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_display_name_too_long(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["display_name"] = self.random_string(51)
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_display_name_length_equal_to_minimum(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["display_name"] = self.random_string(1)
        self.assert_sign_up_successful(data=data)

    def test_sign_up_display_name_length_equal_to_maximum(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["display_name"] = self.random_string(50)
        self.assert_sign_up_successful(data=data)

    def test_sign_up_no_password_and_confirmation(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["password"] = ""
        data["confirmation"] = ""
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_password_and_confirmation_too_short(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        password = self.random_string(5)
        data["password"] = password
        data["confirmation"] = password
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_password_and_confirmation_length_equal_to_minimum(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        password = self.random_string(6)
        data["password"] = password
        data["confirmation"] = password
        self.assert_sign_up_successful(data=data)

    def test_sign_up_password_and_confirmation_dont_match(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["password"] = "password"
        data["confirmation"] = "wordpass"
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_account_already_exists(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        data["email"] = self.email
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_success(self):
        self.sign_out()
        data = self.get_mock_sign_up_data()
        self.assert_sign_up_successful(data=data)

    """
    Sign in tests.
    """

    def assert_sign_in_successful(self, data):
        response = self.client.post("/user/sign-in", data=data)
        self.assertEqual(response.status_code, 302)

    def assert_sign_in_unsuccessful(self, data):
        response = self.client.post("/user/sign-in", data=data)
        self.assertEqual(response.status_code, 200)

    def test_sign_in_already_signed_in(self):
        response = self.client.get("/user/sign-in")
        self.assertEqual(response.status_code, 302)

    def test_sign_in_GET(self):
        self.sign_out()
        response = self.client.get("/user/sign-in")
        self.assertEqual(response.status_code, 200)

    def test_sign_in_no_email(self):
        self.sign_out()
        data = self.get_mock_sign_in_data()
        data["email"] = ""
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_invalid_email(self):
        self.sign_out()
        data = self.get_mock_sign_in_data()
        data["email"] = "invalid"
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_account_does_not_exist(self):
        self.sign_out()
        data = self.get_mock_sign_in_data()
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_no_password(self):
        self.sign_out()
        data = self.get_mock_sign_in_data()
        data["password"] = ""
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_incorrect_password(self):
        self.sign_out()
        data = {"email": self.email, "password": self.random_string(7)}
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_success(self):
        self.sign_out()
        data = {"email": self.email, "password": self.password}
        self.assert_sign_in_successful(data=data)

    """
    Sign out tests.
    """

    def test_sign_out_POST(self):
        response = self.client.post("/user/sign-out")
        self.assertEqual(response.status_code, 200)

    def test_sign_out_GET(self):
        response = self.client.get("/user/sign-out")
        self.assertEqual(response.status_code, 200)

    """
    Show tests.
    """

    def test_show_invalid_id(self):
        response = self.client.get("/user/1/show")
        self.assertEqual(response.status_code, 302)

    def test_show_no_user_with_id(self):
        response = self.client.get("/user/5a09bcdff3853517be67e293/show")
        self.assertEqual(response.status_code, 302)

    def test_show_success(self):
        response = self.client.get("/user/{}/show".format(str(self.user.id)))
        self.assertEqual(response.status_code, 200)

    """
    Settings tests.
    """

    def test_settings_sign_in_required(self):
        self.sign_out()
        response = self.client.get("/user/settings")
        self.assertEqual(response.status_code, 302)

    def test_settings_GET(self):
        response = self.client.get("/user/settings")
        self.assertEqual(response.status_code, 200)

    """
    Update profile tests.
    """

    def assert_update_profile_successful(self, data):
        response = self.client.post("/user/update-profile", data=data)
        user = User.objects(email=self.email).first()
        self.assertEqual(user.display_name, data["display_name"])
        self.assertEqual(user.avatar_url, data["avatar_url"])
        self.assertEqual(user.bio, data["bio"])
        self.assertEqual(response.status_code, 302)

    def assert_update_profile_unsuccessful(self, data):
        response = self.client.post("/user/update-profile", data=data)
        self.assertEqual(response.status_code, 200)

    def test_update_profile_sign_in_required(self):
        self.sign_out()
        response = self.client.get("/user/update-profile")
        self.assertEqual(response.status_code, 302)

    def test_update_profile_GET(self):
        response = self.client.get("/user/update-profile")
        self.assertEqual(response.status_code, 200)

    def test_update_profile_no_display_name(self):
        data = self.get_mock_update_profile_data()
        data["display_name"] = ""
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_display_name_too_long(self):
        data = self.get_mock_update_profile_data()
        data["display_name"] = self.random_string(51)
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_display_name_length_equal_to_minimum(self):
        data = self.get_mock_update_profile_data()
        data["display_name"] = self.random_string(1)
        self.assert_update_profile_successful(data=data)

    def test_update_profile_display_name_length_equal_to_maximum(self):
        data = self.get_mock_update_profile_data()
        data["display_name"] = self.random_string(50)
        self.assert_update_profile_successful(data=data)

    def test_update_profile_no_avatar_url(self):
        data = self.get_mock_update_profile_data()
        data["avatar_url"] = ""
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_invalid_avatar_url(self):
        data = self.get_mock_update_profile_data()
        data["avatar_url"] = "invalid"
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_bio_too_long(self):
        data = self.get_mock_update_profile_data()
        data["bio"] = self.random_string(161)
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_bio_length_equal_to_maximum(self):
        data = self.get_mock_update_profile_data()
        data["bio"] = self.random_string(160)
        self.assert_update_profile_successful(data=data)

    def test_update_profile_success(self):
        data = self.get_mock_update_profile_data()
        self.assert_update_profile_successful(data=data)

    """
    Update password tests.
    """

    def assert_update_password_successful(self, data):
        response = self.client.post("/user/update-password", data=data)
        user = User.objects(email=self.email).first()
        self.assertFalse(sha256_crypt.verify(data["current_password"], user.password))
        self.assertTrue(sha256_crypt.verify(data["new_password"], user.password))
        self.assertEqual(response.status_code, 302)

    def assert_update_password_unsuccessful(self, data):
        response = self.client.post("/user/update-password", data=data)
        self.assertEqual(response.status_code, 200)

    def test_update_password_sign_in_required(self):
        self.sign_out()
        response = self.client.get("/user/update-password")
        self.assertEqual(response.status_code, 302)

    def test_update_password_GET(self):
        response = self.client.get("/user/update-password")
        self.assertEqual(response.status_code, 200)

    def test_update_password_no_current_password(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = ""
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_incorrect_current_password(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = "incorrect"
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_no_new_password_and_confirmation(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = self.password
        data["new_password"] = ""
        data["confirmation"] = ""
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_new_password_and_confirmation_too_short(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = self.password
        password = self.random_string(5)
        data["new_password"] = password
        data["confirmation"] = password
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_new_password_and_confirmation_length_equal_to_minimum(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = self.password
        password = self.random_string(6)
        data["new_password"] = password
        data["confirmation"] = password
        self.assert_update_password_successful(data=data)

    def test_update_password_new_password_and_confirmation_dont_match(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = self.password
        data["new_password"] = "password"
        data["confirmation"] = "wordpass"
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_success(self):
        data = self.get_mock_update_password_data()
        data["current_password"] = self.password
        self.assert_update_password_successful(data=data)

    """
    Delete tests.
    """

    def test_delete_sign_in_required(self):
        self.sign_out()
        response = self.client.post("/user/delete")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_delete_GET(self):
        response = self.client.get("/user/delete")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_delete_success(self):
        response = self.client.post("/user/delete")
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

    """
    Posts tests.
    """

    def test_posts_invalid_id(self):
        response = self.client.get("/user/1/posts")
        self.assertEqual(response.status_code, 302)

    def test_posts_no_user_with_id(self):
        response = self.client.get("/user/5a09bcdff3853517be67e293/posts")
        self.assertEqual(response.status_code, 302)

    def test_posts_success(self):
        # create user posts
        for i in range(4):
            self.get_mock_post(author=self.user).save()

        # create other posts
        for i in range(6):
            self.get_mock_post().save()

        response = self.client.get("/user/{}/posts".format(str(self.user.id)))

        # ensure only posts for specified user are returned
        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 4)

        self.assertEqual(response.status_code, 200)

class PostTest(TestCase):
    """
    Create tests.
    """

    def assert_create_successful(self, data):
        response = self.client.post("/post/create", data=data)
        post = Post.objects.first()
        self.assertEqual(post.author.id, self.user.id)
        self.assertEqual(post.title, data["title"])
        self.assertEqual(post.lead_paragraph, data["lead_paragraph"])
        self.assertEqual(post.image_url, data["image_url"])
        self.assertEqual(post.content, data["content"])
        self.assertIsNotNone(post.created)
        self.assertIsNone(post.last_updated)

    def assert_create_unsuccessful(self, data):
        response = self.client.post("/post/create", data=data)
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_create_sign_in_required(self):
        self.sign_out()
        response = self.client.post("/post/create")
        self.assertEqual(response.status_code, 302)

    def test_create_GET(self):
        response = self.client.get("/post/create")
        self.assertEqual(response.status_code, 200)

    def test_create_no_title(self):
        data = self.get_mock_post_data()
        data["title"] = ""
        self.assert_create_unsuccessful(data=data)

    def test_create_title_too_long(self):
        data = self.get_mock_post_data()
        data["title"] = self.random_string(161)
        self.assert_create_unsuccessful(data=data)

    def test_create_title_length_equal_to_minimum(self):
        data = self.get_mock_post_data()
        data["title"] = self.random_string(1)
        self.assert_create_successful(data=data)

    def test_create_title_length_equal_to_maximum(self):
        data = self.get_mock_post_data()
        data["title"] = self.random_string(160)
        self.assert_create_successful(data=data)

    def test_create_lead_paragraph_too_long(self):
        data = self.get_mock_post_data()
        data["lead_paragraph"] = self.random_string(501)
        self.assert_create_unsuccessful(data=data)

    def test_create_lead_paragraph_length_equal_to_maximum(self):
        data = self.get_mock_post_data()
        data["lead_paragraph"] = self.random_string(500)
        self.assert_create_successful(data=data)

    def test_create_no_image_url(self):
        data = self.get_mock_post_data()
        data["image_url"] = ""
        self.assert_create_unsuccessful(data=data)

    def test_create_invalid_image_url(self):
        data = self.get_mock_post_data()
        data["image_url"] = "invalid"
        self.assert_create_unsuccessful(data=data)

    def test_create_no_content(self):
        data = self.get_mock_post_data()
        data["content"] = ""
        self.assert_create_unsuccessful(data=data)

    def test_create_content_too_long(self):
        data = self.get_mock_post_data()
        data["content"] = self.random_string(10_001)
        self.assert_create_unsuccessful(data=data)

    def test_create_content_length_equal_to_minimum(self):
        data = self.get_mock_post_data()
        data["content"] = self.random_string(1)
        self.assert_create_successful(data=data)

    def test_create_content_length_equal_to_maximum(self):
        data = self.get_mock_post_data()
        data["content"] = self.random_string(10_000)
        self.assert_create_successful(data=data)

    def test_create_success(self):
        data = self.get_mock_post_data()
        self.assert_create_successful(data=data)

    """
    Show tests.
    """

    def test_show_invalid_id(self):
        response = self.client.get("/post/1/show")
        self.assertEqual(response.status_code, 302)

    def test_show_no_post_with_id(self):
        response = self.client.get("/post/5a09bcdff3853517be67e293/show")
        self.assertEqual(response.status_code, 302)

    def test_show_success(self):
        post = self.get_mock_post().save()
        response = self.client.get("/post/{}/show".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    """
    Settings tests.
    """

    def test_settings_sign_in_required(self):
        self.sign_out()
        post = self.get_mock_post(author=self.user).save()
        response = self.client.get("/post/{}/settings".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_settings_invalid_id(self):
        response = self.client.get("/post/1/settings")
        self.assertEqual(response.status_code, 302)

    def test_settings_no_post_with_id(self):
        response = self.client.get("/post/5a09bcdff3853517be67e293/settings")
        self.assertEqual(response.status_code, 302)

    def test_settings_not_the_author(self):
        post = self.get_mock_post().save()
        response = self.client.get("/post/{}/settings".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_settings_success(self):
        post = self.get_mock_post(author=self.user).save()
        response = self.client.get("/post/{}/settings".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    """
    Update tests
    """

    def test_update_sign_in_required(self):
        self.sign_out()
        post = self.get_mock_post(author=self.user).save()
        response = self.client.get("/post/{}/update".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_update_invalid_id(self):
        response = self.client.get("/post/1/update")
        self.assertEqual(response.status_code, 302)

    def test_update_no_post_with_id(self):
        response = self.client.get("/post/5a09bcdff3853517be67e293/update")
        self.assertEqual(response.status_code, 302)

    def test_update_not_the_author(self):
        post = self.get_mock_post().save()
        response = self.client.get("/post/{}/update".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_update_GET(self):
        post = self.get_mock_post(author=self.user).save()
        response = self.client.get("/post/{}/update".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    def test_update_success(self):
        post = self.get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        response = self.client.post("/post/{}/update".format(str(post.id)), data=data)
        post = Post.objects(id=str(post.id)).first()
        self.assertEqual(post.author.id, self.user.id)
        self.assertEqual(post.title, data["title"])
        self.assertEqual(post.lead_paragraph, data["lead_paragraph"])
        self.assertEqual(post.image_url, data["image_url"])
        self.assertEqual(post.content, data["content"])
        self.assertIsNotNone(post.created)
        self.assertIsNotNone(post.last_updated)
        self.assertEqual(response.status_code, 302)

    """
    Delete tests.
    """

    def test_delete_sign_in_required(self):
        self.sign_out()
        post = self.get_mock_post(author=self.user).save()
        response = self.client.get("/post/{}/delete".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_delete_invalid_id(self):
        response = self.client.get("/post/1/delete")
        self.assertEqual(response.status_code, 302)

    def test_delete_no_post_with_id(self):
        response = self.client.get("/post/5a09bcdff3853517be67e293/delete")
        self.assertEqual(response.status_code, 302)

    def test_delete_not_the_author(self):
        post = self.get_mock_post().save()
        response = self.client.get("/post/{}/delete".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_delete_GET(self):
        post = self.get_mock_post(author=self.user).save()
        response = self.client.get("/post/{}/delete".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    def test_delete_success(self):
        post = self.get_mock_post(author=self.user).save()
        response = self.client.post("/post/{}/delete".format(str(post.id)))
        self.assertIsNone(Post.objects(id=post.id).first())
        self.assertEqual(response.status_code, 302)

    """
    Latest tests.
    """

    def test_latest_success(self):
        # create posts
        for i in range(16):
            self.get_mock_post().save()

        # assert that we get first page of results
        response = self.client.get("/post/latest?limit=10&skip=0")

        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 10)

        self.assertEqual(response.status_code, 200)

        # assert that we get the second page of results
        response = self.client.get("/post/latest?limit=10&skip=10")

        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 6)

        self.assertEqual(response.status_code, 200)

    """
    Get comments tests.
    """

    def test_get_comments_invalid_id(self):
        response = self.client.get("/post/1/comments")
        self.assertEqual(response.status_code, 302)

    def test_get_comments_no_post_with_id(self):
        response = self.client.get("/post/5a09bcdff3853517be67e293/comments")
        self.assertEqual(response.status_code, 302)

    def test_get_comments_success(self):
        # create post and comments
        post = self.get_mock_post().save()
        for i in range(4):
            self.get_mock_comment(post=post).save()

        # create another post and comments
        another_post = self.get_mock_post().save()
        for i in range(6):
            self.get_mock_comment(post=another_post).save()

        response = self.client.get("/post/{}/comments".format(str(post.id)))

        # ensure only comments for specified post are returned
        comments = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(comments), 4)

        self.assertEqual(response.status_code, 200)

    """
    Create comment tests.
    """

    def test_create_comment_sign_in_required(self):
        self.sign_out()
        data = self.get_mock_comment_data()
        response = self.client.post("/post/5a09bcdff3853517be67e293/comment", data=data)
        self.assertEqual(response.status_code, 302)

    def test_create_comment_invalid_id(self):
        data = self.get_mock_comment_data()
        response = self.client.post("/post/1/comment", data=data)
        self.assertEqual(response.status_code, 302)

    def test_create_comment_no_post_with_id(self):
        data = self.get_mock_comment_data()
        response = self.client.post("/post/5a09bcdff3853517be67e293/comment", data=data)
        self.assertEqual(response.status_code, 302)

    def test_create_comment_no_text(self):
        post = self.get_mock_post().save()
        data = self.get_mock_comment_data()
        data["text"] = ""
        response = self.client.post("/post/{}/comment".format(str(post.id)), data=data)
        self.assertEqual(response.status_code, 400)

    def test_create_comment_text_too_long(self):
        post = self.get_mock_post().save()
        data = self.get_mock_comment_data()
        data["text"] = self.random_string(501)
        response = self.client.post("/post/{}/comment".format(str(post.id)), data=data)
        self.assertEqual(response.status_code, 400)

    def test_create_comment_text_length_equal_to_minimum(self):
        post = self.get_mock_post().save()
        data = {"text": self.random_string(1)}
        response = self.client.post("/post/{}/comment".format(str(post.id)), data=data)
        comment = Comment.objects(post=post.id).first()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.text, data["text"])
        self.assertIsNotNone(comment.created)
        self.assertEqual(response.status_code, 200)

    def test_create_comment_text_length_equal_to_maximum(self):
        post = self.get_mock_post().save()
        data = {"text": self.random_string(500)}
        response = self.client.post("/post/{}/comment".format(str(post.id)), data=data)
        comment = Comment.objects(post=post.id).first()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.text, data["text"])
        self.assertIsNotNone(comment.created)
        self.assertEqual(response.status_code, 200)

    def test_create_comment_success(self):
        post = self.get_mock_post().save()
        data = {"text": self.random_string(7)}
        response = self.client.post("/post/{}/comment".format(str(post.id)), data=data)
        comment = Comment.objects(post=post.id).first()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.text, data["text"])
        self.assertIsNotNone(comment.created)
        self.assertEqual(response.status_code, 200)

    """
    Preview tests.
    """

    def test_preview_no_content(self):
        response = self.client.post("/post/preview", data={})
        html = json.loads(response.get_data(as_text=True))["html"]
        self.assertEqual(html, "")
        self.assertEqual(response.status_code, 200)

    def test_preview_success(self):
        response = self.client.post("/post/preview", data={"content": "# Hello"})
        html = json.loads(response.get_data(as_text=True))["html"]
        self.assertEqual(html, "<h1>Hello</h1>\n")
        self.assertEqual(response.status_code, 200)

class SearchTest(TestCase):
    def test_index(self):
        response = self.client.get("/search")
        self.assertEqual(response.status_code, 200)

    def test_no_search_terms(self):
        response = self.client.get("/search?terms=", headers={"accept": "application/json"})
        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 0)
        self.assertEqual(response.status_code, 200)

    @mock.patch("tiny.blueprints.search.search_posts")
    def test_search_success(self, mock_search_posts):
        term = "python"

        # create posts containing search term
        mocked_posts = []
        for i in range(4):
            post = self.get_mock_post()
            post.content = term
            post.save()
            mocked_posts.append(post)

        mock_search_posts.return_value = mocked_posts

        response = self.client.get("/search?terms={}".format(term),
                                headers={"accept": "application/json"})

        # ensure only posts containing specified term are returned
        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 4)

        self.assertEqual(response.status_code, 200)
