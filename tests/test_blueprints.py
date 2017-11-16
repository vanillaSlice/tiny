import json
from unittest import TestCase

from passlib.hash import sha256_crypt

from tiny.models import Comment, Post, User
from . import (clear_db,
               get_mock_comment,
               get_mock_post_data,
               get_mock_post,
               get_mock_sign_in_data,
               get_mock_sign_up_data,
               get_mock_update_profile_data,
               get_mock_user,
               get_test_client,
               random_email,
               random_string)

class BlueprintTest(TestCase):
    def setUp(self):
        self.app = get_test_client()

        # make sure we set up a user and sign in
        self.email = "me@example.com"
        self.password = "password"
        self.user = get_mock_user()
        self.user.email = self.email
        self.user.password = sha256_crypt.hash("password")
        self.user.save()
        self.sign_in({"email": self.email, "password": self.password})

    def tearDown(self):
        clear_db()
        self.sign_out()

    def sign_in(self, data):
        return self.app.post("/user/sign-in", data=data)

    def sign_out(self):
        return self.app.post("/user/sign-out")

class HomeTest(BlueprintTest):
    def test_index(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

class UserTest(BlueprintTest):
    """
    Sign up tests.
    """

    def test_sign_up_already_signed_in(self):
        response = self.app.get("/user/sign-up")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_sign_up_GET(self):
        self.sign_out()
        response = self.app.get("/user/sign-up")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_invalid_form(self):
        self.sign_out()
        response = self.app.post("/user/sign-up", data={})
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_account_already_exists(self):
        self.sign_out()
        form = get_mock_sign_up_data()
        form["email"] = self.email
        response = self.app.post("/user/sign-up", data=form)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_success(self):
        self.sign_out()
        response = self.app.post("/user/sign-up", data=get_mock_sign_up_data())
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, 302)

    """
    Sign in tests.
    """

    def test_sign_in_already_signed_in(self):
        response = self.app.get("/user/sign-in")
        self.assertEqual(response.status_code, 302)

    def test_sign_in_GET(self):
        self.sign_out()
        response = self.app.get("/user/sign-in")
        self.assertEqual(response.status_code, 200)

    def test_sign_in_invalid_form(self):
        self.sign_out()
        response = self.sign_in(data={})
        self.assertEqual(response.status_code, 200)

    def test_sign_in_account_does_not_exist(self):
        self.sign_out()
        response = self.sign_in(data=get_mock_sign_in_data())
        self.assertEqual(response.status_code, 200)

    def test_sign_in_incorrect_password(self):
        self.sign_out()
        response = self.sign_in(data={"email": self.email, "password": random_string(7)})
        self.assertEqual(response.status_code, 200)

    def test_sign_in_success(self):
        self.sign_out()
        response = self.sign_in(data={"email": self.email, "password": self.password})
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
    Show tests.
    """

    def test_show_invalid_id(self):
        response = self.app.get("/user/1/show")
        self.assertEqual(response.status_code, 302)

    def test_show_no_user_with_id(self):
        response = self.app.get("/user/5a09bcdff3853517be67e293/show")
        self.assertEqual(response.status_code, 302)

    def test_show_success(self):
        response = self.app.get("/user/{}/show".format(str(self.user.id)))
        self.assertEqual(response.status_code, 200)

    """
    Settings tests.
    """

    def test_settings_sign_in_required(self):
        self.sign_out()
        response = self.app.get("/user/settings")
        self.assertEqual(response.status_code, 302)

    def test_settings_GET(self):
        response = self.app.get("/user/settings")
        self.assertEqual(response.status_code, 200)

    """
    Update profile tests.
    """

    def test_update_profile_sign_in_required(self):
        self.sign_out()
        response = self.app.get("/user/update-profile")
        self.assertEqual(response.status_code, 302)

    def test_update_profile_GET(self):
        response = self.app.get("/user/update-profile")
        self.assertEqual(response.status_code, 200)

    def test_update_profile_invalid_form(self):
        response = self.app.post("/user/update-profile", data={})
        self.assertEqual(response.status_code, 200)

    def test_update_profile_success(self):
        form = get_mock_update_profile_data()
        response = self.app.post("/user/update-profile", data=form)
        user = User.objects(email=self.email).first()
        self.assertEqual(user.display_name, form["display_name"])
        self.assertEqual(user.avatar_url, form["avatar_url"])
        self.assertEqual(user.bio, form["bio"])
        self.assertEqual(response.status_code, 302)

    """
    Update password tests.
    """

    def test_update_password_sign_in_required(self):
        self.sign_out()
        response = self.app.get("/user/update-password")
        self.assertEqual(response.status_code, 302)

    def test_update_password_GET(self):
        response = self.app.get("/user/update-password")
        self.assertEqual(response.status_code, 200)

    def test_update_password_invalid_form(self):
        response = self.app.post("/user/update-password", data={})
        self.assertEqual(response.status_code, 200)

    def test_update_password_incorrect_password(self):
        form = {
            "current_password": "incorrect",
            "new_password": "new_password",
            "confirmation": "new_password"
        }
        response = self.app.post("/user/update-password", data=form)
        self.assertEqual(response.status_code, 200)

    def test_update_password_success(self):
        # update the password
        new_password = "new password"
        form = {
            "current_password": self.password,
            "new_password": new_password,
            "confirmation": new_password
        }
        response = self.app.post("/user/update-password", data=form)
        self.assertEqual(response.status_code, 302)

        self.sign_out()

        # try to sign in with old password
        form = {
            "email": self.email,
            "password": self.password
        }
        response = self.app.post("/user/sign-in", data=form)
        self.assertEqual(response.status_code, 200)

        # sign in with new password
        form["password"] = new_password
        response = self.app.post("/user/sign-in", data=form)
        self.assertEqual(response.status_code, 302)

    """
    Delete tests.
    """

    def test_delete_sign_in_required(self):
        self.sign_out()
        response = self.app.post("/user/delete")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_delete_GET(self):
        response = self.app.get("/user/delete")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_delete_success(self):
        response = self.app.post("/user/delete")
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

    """
    Posts tests.
    """

    def test_posts_invalid_id(self):
        response = self.app.get("/user/1/posts")
        self.assertEqual(response.data, b'{\n  "error message": "invalid author id 1"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_posts_invalid_size(self):
        response = self.app.get("/user/{}/posts?size=a".format(str(self.user.id)))
        self.assertEqual(response.data, b'{\n  "error message": "invalid size a"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_posts_invalid_offset(self):
        response = self.app.get("/user/{}/posts?offset=b".format(str(self.user.id)))
        self.assertEqual(response.data, b'{\n  "error message": "invalid offset b"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_posts_success(self):
        # create user posts
        for i in range(4):
            get_mock_post(author=self.user).save()

        # create other posts
        for i in range(6):
            get_mock_post().save()

        response = self.app.get("/user/{}/posts".format(str(self.user.id)))

        # ensure only posts for specified user are returned
        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 4)

        self.assertEqual(response.status_code, 200)

class PostTest(BlueprintTest):
    """
    Create tests.
    """
    def test_create_sign_in_required(self):
        self.sign_out()
        response = self.app.post("/post/create")
        self.assertEqual(response.status_code, 302)

    def test_create_GET(self):
        response = self.app.get("/post/create")
        self.assertEqual(response.status_code, 200)

    def test_create_invalid_form(self):
        response = self.app.post("/post/create", data={})
        self.assertEqual(response.status_code, 200)

    def test_create_success(self):
        response = self.app.post("/post/create", data=get_mock_post_data())
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    """
    Show tests.
    """

    def test_show_invalid_id(self):
        response = self.app.get("/post/1/show")
        self.assertEqual(response.status_code, 302)

    def test_show_no_post_with_id(self):
        response = self.app.get("/post/5a09bcdff3853517be67e293/show")
        self.assertEqual(response.status_code, 302)

    def test_show_success(self):
        post = get_mock_post().save()
        response = self.app.get("/post/{}/show".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    """
    Update tests.
    """

    def test_update_sign_in_required(self):
        self.sign_out()
        response = self.app.get("/post/5a09bcdff3853517be67e293/update")
        self.assertEqual(response.status_code, 302)

    def test_update_no_post_with_id(self):
        response = self.app.get("/post/5a09bcdff3853517be67e293/update")
        self.assertEqual(response.status_code, 302)

    def test_update_not_the_author(self):
        post = get_mock_post().save()
        response = self.app.get("/post/{}/update".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_update_GET(self):
        post = get_mock_post(author=self.user).save()
        response = self.app.get("/post/{}/update".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    def test_update_success(self):
        post = get_mock_post(author=self.user).save()
        form = get_mock_post_data()
        response = self.app.post("/post/{}/update".format(str(post.id)), data=form)
        post = Post.objects(id=str(post.id)).first()
        self.assertEqual(post.title, form["title"])
        self.assertEqual(post.preview, form["preview"])
        self.assertEqual(post.image_url, form["image_url"])
        self.assertEqual(post.content, form["content"])
        self.assertIsNotNone(post.last_updated)
        self.assertEqual(response.status_code, 302)

    """
    Delete tests.
    """

    def test_delete_sign_in_required(self):
        self.sign_out()
        response = self.app.get("/post/5a09bcdff3853517be67e293/delete")
        self.assertEqual(response.status_code, 302)

    def test_delete_no_post_with_id(self):
        response = self.app.get("/post/5a09bcdff3853517be67e293/delete")
        self.assertEqual(response.status_code, 302)

    def test_delete_not_the_author(self):
        post = get_mock_post().save()
        response = self.app.get("/post/{}/delete".format(str(post.id)))
        self.assertEqual(response.status_code, 302)

    def test_delete_GET(self):
        post = get_mock_post(author=self.user).save()
        response = self.app.get("/post/{}/delete".format(str(post.id)))
        self.assertEqual(response.status_code, 200)

    def test_delete_success(self):
        post = get_mock_post(author=self.user).save()
        response = self.app.post("/post/{}/delete".format(str(post.id)))
        self.assertIsNone(Post.objects(id=post.id).first())
        self.assertEqual(response.status_code, 302)

    """
    Get comments tests.
    """

    def test_comments_invalid_id(self):
        response = self.app.get("/post/1/comments")
        self.assertEqual(response.data, b'{\n  "error message": "invalid post id 1"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_comments_invalid_size(self):
        response = self.app.get("/post/5a09bcdff3853517be67e293/comments?size=a")
        self.assertEqual(response.data, b'{\n  "error message": "invalid size a"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_comments_invalid_offset(self):
        response = self.app.get("/post/5a09bcdff3853517be67e293/comments?offset=b")
        self.assertEqual(response.data, b'{\n  "error message": "invalid offset b"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_comments_success(self):
        # create post and comments
        post = get_mock_post().save()
        for i in range(4):
            get_mock_comment(post=post).save()

        # create another post and comments
        another_post = get_mock_post().save()
        for i in range(6):
            get_mock_comment(post=another_post).save()

        response = self.app.get("/post/{}/comments".format(str(post.id)))

        # ensure only comments for specified post are returned
        comments = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(comments), 4)

        self.assertEqual(response.status_code, 200)

    """
    Create comment tests.
    """

    def test_comment_sign_in_required(self):
        self.sign_out()
        response = self.app.post("/post/5a09bcdff3853517be67e293/comment")
        self.assertEqual(response.status_code, 302)

    def test_comment_invalid_id(self):
        response = self.app.post("/post/1/comment")
        self.assertEqual(response.data, b'{\n  "error message": "invalid post id 1"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_comment_post_does_not_exist(self):
        response = self.app.post("/post/5a09bcdff3853517be67e293/comment")
        self.assertEqual(response.data,
                         b'{\n  "error message": "post with id 5a09bcdff3853517be67e293 does not exist"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_comment_invalid_form(self):
        post = get_mock_post().save()
        response = self.app.post("/post/{}/comment".format(str(post.id)), data={})
        self.assertEqual(response.status_code, 400)

    def test_comment_success(self):
        post = get_mock_post().save()
        form = {"text": random_string(7)}
        response = self.app.post("/post/{}/comment".format(str(post.id)), data=form)
        comment = Comment.objects(post=post.id).first()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.text, form["text"])
        self.assertIsNotNone(comment.created)
        self.assertEqual(response.status_code, 200)

class SearchTest(BlueprintTest):
    def test_index(self):
        response = self.app.get("/search")
        self.assertEqual(response.status_code, 200)

    def test_query_invalid_size(self):
        response = self.app.get("/search/query?size=a")
        self.assertEqual(response.data, b'{\n  "error message": "invalid size a"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_query_invalid_offset(self):
        response = self.app.get("/search/query?offset=b")
        self.assertEqual(response.data, b'{\n  "error message": "invalid offset b"\n}\n')
        self.assertEqual(response.status_code, 400)

    def test_query_success(self):
        term = "python"

        # create posts containing search term
        for i in range(4):
            post = get_mock_post()
            post.content = term
            post.save()

        # create other posts
        for i in range(6):
            get_mock_post().save()

        # using query terms
        response = self.app.get("/search/query?terms={}".format(term))

        # ensure only posts containing specified term are returned
        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 4)

        self.assertEqual(response.status_code, 200)

        # without query terms
        response = self.app.get("/search/query")

        # ensure all posts are returned
        posts = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(posts), 10)

        self.assertEqual(response.status_code, 200)
