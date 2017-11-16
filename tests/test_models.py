from unittest import TestCase

from mongoengine.errors import ValidationError

from . import (clear_db,
               get_db_connection,
               get_mock_comment,
               get_mock_post,
               get_mock_user,
               random_string)

class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = get_db_connection()

    def tearDown(self):
        clear_db()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def assert_validation_error(self, model):
        self.assertRaises(ValidationError, model.validate)

class UserTest(ModelTest):
    def setUp(self):
        self.user = get_mock_user()

    def test_user_no_email(self):
        del self.user.email
        self.assert_validation_error(self.user)

    def test_user_no_password(self):
        del self.user.password
        self.assert_validation_error(self.user)

    def test_user_no_display_name(self):
        del self.user.display_name
        self.assert_validation_error(self.user)

    def test_user_display_name_too_short(self):
        self.user.display_name = ""
        self.assert_validation_error(self.user)

    def test_user_display_name_too_long(self):
        self.user.display_name = random_string(21)
        self.assert_validation_error(self.user)

    def test_user_display_name_length_equal_to_minimum(self):
        self.user.display_name = random_string(1)
        self.user.validate()

    def test_user_display_name_length_equal_to_maximum(self):
        self.user.display_name = random_string(20)
        self.user.validate()

    def test_user_bio_too_long(self):
        self.user.bio = random_string(161)
        self.assert_validation_error(self.user)

    def test_user_bio_length_equal_to_maximum(self):
        self.user.bio = random_string(160)
        self.user.validate()

    def test_user_valid(self):
        self.user.validate()

class PostTest(ModelTest):
    def setUp(self):
        self.post = get_mock_post()

    def tearDown(self):
        clear_db()

    def test_post_no_author(self):
        del self.post.author
        self.assert_validation_error(self.post)

    def test_post_no_title(self):
        del self.post.title
        self.assert_validation_error(self.post)

    def test_post_title_too_short(self):
        self.post.title = ""
        self.assert_validation_error(self.post)

    def test_post_title_too_long(self):
        self.post.title = random_string(101)
        self.assert_validation_error(self.post)

    def test_post_title_length_equal_to_minimum(self):
        self.post.title = random_string(1)
        self.post.validate()

    def test_post_title_length_equal_to_maximum(self):
        self.post.title = random_string(100)
        self.post.validate()

    def test_post_preview_too_long(self):
        self.post.preview = random_string(101)
        self.assert_validation_error(self.post)

    def test_post_preview_length_equal_to_maximum(self):
        self.post.preview = random_string(100)
        self.post.validate()

    def test_post_no_content(self):
        del self.post.content
        self.assert_validation_error(self.post)

    def test_post_content_too_short(self):
        self.post.content = ""
        self.assert_validation_error(self.post)

    def test_post_content_too_long(self):
        self.post.content = random_string(10_001)
        self.assert_validation_error(self.post)

    def test_post_content_length_equal_to_minimum(self):
        self.post.content = random_string(1)
        self.post.validate()

    def test_post_content_length_equal_to_maximum(self):
        self.post.content = random_string(10_000)
        self.post.validate()

    def test_post_valid(self):
        self.post.validate()

class CommentTest(ModelTest):
    def setUp(self):
        self.comment = get_mock_comment()

    def test_comment_no_author(self):
        del self.comment.author
        self.assert_validation_error(self.comment)

    def test_comment_no_post(self):
        del self.comment.post
        self.assert_validation_error(self.comment)

    def test_comment_no_text(self):
        del self.comment.text
        self.assert_validation_error(self.comment)

    def test_comment_text_too_short(self):
        self.comment.text = ""
        self.assert_validation_error(self.comment)

    def test_comment_text_too_long(self):
        self.comment.text = random_string(321)
        self.assert_validation_error(self.comment)

    def test_comment_text_length_equal_to_minimum(self):
        self.comment.text = random_string(1)
        self.comment.validate()

    def test_comment_text_length_equal_to_maximum(self):
        self.comment.text = random_string(320)
        self.comment.validate()

    def test_comment_valid(self):
        self.comment.validate()
