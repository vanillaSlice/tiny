from unittest import TestCase

from . import (get_mock_comment_form,
               get_mock_post_form,
               get_mock_sign_in_form,
               get_mock_sign_up_form,
               get_mock_update_password_form,
               get_mock_update_profile_form,
               random_string)

class FormTest(TestCase):
    def assert_valid(self):
        self.assertTrue(self.form.validate())

    def assert_invalid(self):
        self.assertFalse(self.form.validate())

class SignUpFormTest(FormTest):
    def setUp(self):
        self.form = get_mock_sign_up_form()

    def test_no_email(self):
        self.form.email.data = ""
        self.assert_invalid()

    def test_invalid_email(self):
        self.form.email.data = "invalid"
        self.assert_invalid()

    def test_no_display_name(self):
        self.form.display_name.data = ""
        self.assert_invalid()

    def test_display_name_too_long(self):
        self.form.display_name.data = random_string(21)
        self.assert_invalid()

    def test_display_name_length_equal_to_minimum(self):
        self.form.display_name.data = random_string(1)
        self.assert_valid()

    def test_display_name_length_equal_to_maximum(self):
        self.form.display_name.data = random_string(20)
        self.assert_valid()

    def test_no_password(self):
        self.form.password.data = ""
        self.form.confirmation.data = ""
        self.assert_invalid()

    def test_password_too_short(self):
        password = random_string(5)
        self.form.password.data = password
        self.form.confirmation.data = password
        self.assert_invalid()

    def test_password_too_long(self):
        password = random_string(21)
        self.form.password.data = password
        self.form.confirmation.data = password
        self.assert_invalid()

    def test_password_length_equal_to_minimum(self):
        password = random_string(6)
        self.form.password.data = password
        self.form.confirmation.data = password
        self.assert_valid()

    def test_password_length_equal_to_maximum(self):
        password = random_string(20)
        self.form.password.data = password
        self.form.confirmation.data = password
        self.assert_valid()

    def test_password_and_confirmation_dont_match(self):
        self.form.password.data = "dont"
        self.form.confirmation.data = "match"
        self.assert_invalid()

    def test_success(self):
        self.assert_valid()

class SignInFormTest(FormTest):
    def setUp(self):
        self.form = get_mock_sign_in_form()

    def test_no_email(self):
        self.form.email.data = ""
        self.assert_invalid()

    def test_invalid_email(self):
        self.form.email.data = "invalid"
        self.assert_invalid()

    def test_no_password(self):
        self.form.password.data = ""
        self.assert_invalid()

    def test_success(self):
        self.assert_valid()

class UpdateProfileFormTest(FormTest):
    def setUp(self):
        self.form = get_mock_update_profile_form()

    def test_no_display_name(self):
        self.form.display_name.data = ""
        self.assert_invalid()

    def test_display_name_too_long(self):
        self.form.display_name.data = random_string(21)
        self.assert_invalid()

    def test_display_name_length_equal_to_minimum(self):
        self.form.display_name.data = random_string(1)
        self.assert_valid()

    def test_display_name_length_equal_to_maximum(self):
        self.form.display_name.data = random_string(20)
        self.assert_valid()

    def test_bio_too_long(self):
        self.form.bio.data = random_string(161)
        self.assert_invalid()

    def test_bio_equal_to_maximum(self):
        self.form.bio.data = random_string(160)
        self.assert_valid()

    def test_success(self):
        self.assert_valid()

class UpdatePasswordFormTest(FormTest):
    def setUp(self):
        self.form = get_mock_update_password_form()

    def test_no_current_password(self):
        self.form.current_password.data = ""
        self.assert_invalid()

    def test_no_new_password(self):
        self.form.new_password.data = ""
        self.form.confirmation.data = ""
        self.assert_invalid()

    def test_new_password_too_short(self):
        password = random_string(5)
        self.form.new_password.data = password
        self.form.confirmation.data = password
        self.assert_invalid()

    def test_new_password_too_long(self):
        password = random_string(21)
        self.form.new_password.data = password
        self.form.confirmation.data = password
        self.assert_invalid()

    def test_new_password_length_equal_to_minimum(self):
        password = random_string(6)
        self.form.new_password.data = password
        self.form.confirmation.data = password
        self.assert_valid()

    def test_new_password_length_equal_to_maximum(self):
        password = random_string(20)
        self.form.new_password.data = password
        self.form.confirmation.data = password
        self.assert_valid()

    def test_new_password_and_confirmation_dont_match(self):
        self.form.new_password.data = "dont"
        self.form.confirmation.data = "match"
        self.assert_invalid()

    def test_success(self):
        self.assert_valid()

class PostFormTest(FormTest):
    def setUp(self):
        self.form = get_mock_post_form()

    def test_no_title(self):
        self.form.title.data = ""
        self.assert_invalid()

    def test_title_too_long(self):
        self.form.title.data = random_string(101)
        self.assert_invalid()

    def test_title_length_equal_to_minimum(self):
        self.form.title.data = random_string(1)
        self.assert_valid()

    def test_title_length_equal_to_maximum(self):
        self.form.title.data = random_string(100)
        self.assert_valid()

    def test_preview_too_long(self):
        self.form.preview.data = random_string(101)
        self.assert_invalid()

    def test_preview_length_equal_to_maximum(self):
        self.form.preview.data = random_string(100)
        self.assert_valid()

    def test_no_content(self):
        self.form.content.data = ""
        self.assert_invalid()

    def test_content_too_long(self):
        self.form.content.data = random_string(10_001)
        self.assert_invalid()

    def test_content_length_equal_to_minimum(self):
        self.form.content.data = random_string(1)
        self.assert_valid()

    def test_content_length_equal_to_maximum(self):
        self.form.content.data = random_string(10_000)
        self.assert_valid()

    def test_success(self):
        self.assert_valid()

class CommentFormTest(FormTest):
    def setUp(self):
        self.form = get_mock_comment_form()

    def test_no_text(self):
        self.form.text.data = ""
        self.assert_invalid()

    def test_text_too_long(self):
        self.form.text.data = random_string(321)
        self.assert_invalid()

    def test_title_length_equal_to_minimum(self):
        self.form.text.data = random_string(1)
        self.assert_valid()

    def test_title_length_equal_to_maximum(self):
        self.form.text.data = random_string(320)
        self.assert_valid()

    def test_success(self):
        self.assert_valid()
