import json

from passlib.hash import sha256_crypt

from tests.test_utils import get_mock_post, random_email, random_string, random_url, sign_out, TestBase
from tiny.models import User

class TestUser(TestBase):

    #
    # Sign up tests.
    #

    def get_mock_sign_up_data(self):
        password = random_string(10)
        return {'email': random_email(),
                'display_name': random_string(10),
                'password': password,
                'confirmation': password}

    def assert_sign_up_successful(self, data):
        response = self.client.post('/user/sign-up', data=data)
        user = User.objects(email=data['email']).first()
        assert sha256_crypt.verify(data['password'], user.password)
        assert user.display_name == data['display_name']
        assert user.bio is None
        assert '/static/images/default-avatar.jpg' in user.avatar_url
        assert user.created is not None
        assert response.status_code == 302

    def assert_sign_up_unsuccessful(self, data):
        response = self.client.post('/user/sign-up', data=data)
        assert User.objects.count() == 1
        assert response.status_code == 400

    def test_sign_up_already_signed_in(self):
        response = self.client.get('/user/sign-up')
        assert response.status_code == 302

    def test_sign_up_GET(self):
        sign_out(self.client)
        response = self.client.get('/user/sign-up')
        assert response.status_code == 200

    def test_sign_up_no_email(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['email'] = ''
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_invalid_email(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['email'] = 'invalid'
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_no_display_name(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['display_name'] = ''
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_display_name_too_long(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['display_name'] = random_string(51)
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_display_name_length_equal_to_minimum(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['display_name'] = random_string(1)
        self.assert_sign_up_successful(data=data)

    def test_sign_up_display_name_length_equal_to_maximum(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['display_name'] = random_string(50)
        self.assert_sign_up_successful(data=data)

    def test_sign_up_no_password_and_confirmation(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['password'] = ''
        data['confirmation'] = ''
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_password_and_confirmation_too_short(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        password = random_string(5)
        data['password'] = password
        data['confirmation'] = password
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_password_and_confirmation_length_equal_to_minimum(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        password = random_string(6)
        data['password'] = password
        data['confirmation'] = password
        self.assert_sign_up_successful(data=data)

    def test_sign_up_password_and_confirmation_dont_match(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['password'] = 'password'
        data['confirmation'] = 'wordpass'
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_account_already_exists(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        data['email'] = self.email
        self.assert_sign_up_unsuccessful(data=data)

    def test_sign_up_success(self):
        sign_out(self.client)
        data = self.get_mock_sign_up_data()
        self.assert_sign_up_successful(data=data)

    #
    # Sign in tests.
    #

    def get_mock_sign_in_data(self):
        return {'email': random_email(),
                'password': random_string(10)}

    def assert_sign_in_successful(self, data):
        response = self.client.post('/user/sign-in', data=data)
        assert response.status_code == 302

    def assert_sign_in_unsuccessful(self, data):
        response = self.client.post('/user/sign-in', data=data)
        assert response.status_code == 400

    def test_sign_in_already_signed_in(self):
        response = self.client.get('/user/sign-in')
        assert response.status_code == 302

    def test_sign_in_GET(self):
        sign_out(self.client)
        response = self.client.get('/user/sign-in')
        assert response.status_code == 200

    def test_sign_in_no_email(self):
        sign_out(self.client)
        data = self.get_mock_sign_in_data()
        data['email'] = ''
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_invalid_email(self):
        sign_out(self.client)
        data = self.get_mock_sign_in_data()
        data['email'] = 'invalid'
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_account_does_not_exist(self):
        sign_out(self.client)
        data = self.get_mock_sign_in_data()
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_no_password(self):
        sign_out(self.client)
        data = self.get_mock_sign_in_data()
        data['password'] = ''
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_incorrect_password(self):
        sign_out(self.client)
        data = {'email': self.email, 'password': random_string(7)}
        self.assert_sign_in_unsuccessful(data=data)

    def test_sign_in_success(self):
        sign_out(self.client)
        data = {'email': self.email, 'password': self.password}
        self.assert_sign_in_successful(data=data)

    #
    # Sign out tests.
    #

    def test_sign_out_POST(self):
        response = self.client.post('/user/sign-out')
        assert response.status_code == 200

    def test_sign_out_GET(self):
        response = self.client.get('/user/sign-out')
        assert response.status_code == 200

    #
    # Show tests.
    #

    def test_show_invalid_id(self):
        response = self.client.get('/user/1/show')
        assert response.status_code == 302

    def test_show_no_user_with_id(self):
        response = self.client.get('/user/5a09bcdff3853517be67e293/show')
        assert response.status_code == 302

    def test_show_success(self):
        response = self.client.get('/user/{}/show'.format(str(self.user.id)))
        assert response.status_code == 200

    #
    # Settings tests.
    #

    def test_settings_sign_in_required(self):
        sign_out(self.client)
        response = self.client.get('/user/settings')
        assert response.status_code == 302

    def test_settings_GET(self):
        response = self.client.get('/user/settings')
        assert response.status_code == 200

    #
    # Update profile tests.
    #

    def get_mock_update_profile_data(self):
        return {'display_name': random_string(10),
                'avatar_url': random_url(),
                'bio': random_string(10)}

    def assert_update_profile_successful(self, data):
        response = self.client.post('/user/update-profile', data=data)
        user = User.objects(email=self.email).first()
        assert user.display_name == data['display_name']
        assert user.avatar_url == data['avatar_url']
        assert user.bio == data['bio']
        assert response.status_code == 302

    def assert_update_profile_unsuccessful(self, data):
        response = self.client.post('/user/update-profile', data=data)
        assert response.status_code == 400

    def test_update_profile_sign_in_required(self):
        sign_out(self.client)
        response = self.client.get('/user/update-profile')
        assert response.status_code == 302

    def test_update_profile_GET(self):
        response = self.client.get('/user/update-profile')
        assert response.status_code == 200

    def test_update_profile_no_display_name(self):
        data = self.get_mock_update_profile_data()
        data['display_name'] = ''
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_display_name_too_long(self):
        data = self.get_mock_update_profile_data()
        data['display_name'] = random_string(51)
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_display_name_length_equal_to_minimum(self):
        data = self.get_mock_update_profile_data()
        data['display_name'] = random_string(1)
        self.assert_update_profile_successful(data=data)

    def test_update_profile_display_name_length_equal_to_maximum(self):
        data = self.get_mock_update_profile_data()
        data['display_name'] = random_string(50)
        self.assert_update_profile_successful(data=data)

    def test_update_profile_no_avatar_url(self):
        data = self.get_mock_update_profile_data()
        data['avatar_url'] = ''
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_invalid_avatar_url(self):
        data = self.get_mock_update_profile_data()
        data['avatar_url'] = 'invalid'
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_bio_too_long(self):
        data = self.get_mock_update_profile_data()
        data['bio'] = random_string(161)
        self.assert_update_profile_unsuccessful(data=data)

    def test_update_profile_bio_length_equal_to_maximum(self):
        data = self.get_mock_update_profile_data()
        data['bio'] = random_string(160)
        self.assert_update_profile_successful(data=data)

    def test_update_profile_success(self):
        data = self.get_mock_update_profile_data()
        self.assert_update_profile_successful(data=data)

    #
    # Update password tests.
    #

    def get_mock_update_password_data(self):
        new_password = random_string(10)
        return {'current_password': random_string(10),
                'new_password': new_password,
                'confirmation': new_password}

    def assert_update_password_successful(self, data):
        response = self.client.post('/user/update-password', data=data)
        user = User.objects(email=self.email).first()
        assert not sha256_crypt.verify(data['current_password'], user.password)
        assert sha256_crypt.verify(data['new_password'], user.password)
        assert response.status_code == 302

    def assert_update_password_unsuccessful(self, data):
        response = self.client.post('/user/update-password', data=data)
        assert response.status_code == 400

    def test_update_password_sign_in_required(self):
        sign_out(self.client)
        response = self.client.get('/user/update-password')
        assert response.status_code == 302

    def test_update_password_GET(self):
        response = self.client.get('/user/update-password')
        assert response.status_code == 200

    def test_update_password_no_current_password(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = ''
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_incorrect_current_password(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = 'incorrect'
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_no_new_password_and_confirmation(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = self.password
        data['new_password'] = ''
        data['confirmation'] = ''
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_new_password_and_confirmation_too_short(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = self.password
        password = random_string(5)
        data['new_password'] = password
        data['confirmation'] = password
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_new_password_and_confirmation_length_equal_to_minimum(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = self.password
        password = random_string(6)
        data['new_password'] = password
        data['confirmation'] = password
        self.assert_update_password_successful(data=data)

    def test_update_password_new_password_and_confirmation_dont_match(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = self.password
        data['new_password'] = 'password'
        data['confirmation'] = 'wordpass'
        self.assert_update_password_unsuccessful(data=data)

    def test_update_password_success(self):
        data = self.get_mock_update_password_data()
        data['current_password'] = self.password
        self.assert_update_password_successful(data=data)

    #
    # Delete tests.
    #

    def test_delete_sign_in_required(self):
        sign_out(self.client)
        response = self.client.post('/user/delete')
        assert User.objects.count() == 1
        assert response.status_code == 302

    def test_delete_GET(self):
        response = self.client.get('/user/delete')
        assert User.objects.count() == 1
        assert response.status_code == 200

    def test_delete_success(self):
        response = self.client.post('/user/delete')
        assert User.objects.count() == 0
        assert response.status_code == 302

    #
    # Posts tests.
    #

    def test_posts_invalid_id(self):
        response = self.client.get('/user/1/posts')
        assert response.status_code == 302

    def test_posts_no_user_with_id(self):
        response = self.client.get('/user/5a09bcdff3853517be67e293/posts')
        assert response.status_code == 302

    def test_posts_success(self):
        # create user posts
        for i in range(4):
            get_mock_post(author=self.user).save()

        # create other posts
        for i in range(6):
            get_mock_post().save()

        response = self.client.get('/user/{}/posts'.format(str(self.user.id)))
        assert response.status_code == 200

        # ensure only posts for specified user are returned
        posts = json.loads(response.get_data(as_text=True))
        assert len(posts) == 4
