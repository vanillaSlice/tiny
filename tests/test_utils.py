import random
import string

from passlib.hash import sha256_crypt

from tiny import create_app
from tiny.models import Comment, Post, User

class TestBase:

    def setup_method(self):
        # set up test app instance
        self.app = create_app(testing=True)
        self.app.app_context().push()
        self.client = self.app.test_client()

        # make sure we set up a user
        self.email = 'me@example.com'
        self.password = 'password'
        self.user = get_mock_user()
        self.user.email = self.email
        self.user.password = sha256_crypt.hash('password')
        self.user.save()

        # make sure we sign in
        sign_in(self.client, self.email, self.password)

    def teardown_method(self):
        clear_db()
        sign_out(self.client)

def clear_db():
    Comment.objects.delete()
    Post.objects.delete()
    User.objects.delete()

def sign_in(client, email, password):
    return client.post('/user/sign-in', data={'email': email, 'password': password})

def sign_out(client):
    return client.post('/user/sign-out')

def random_string(size):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(size))

def random_email():
    return '{}@{}.com'.format(random_string(7), random_string(7))

def random_url():
    return 'http://www.{}.com'.format(random_string(7))

def get_mock_user():
    return User(email=random_email(),
                password=random_string(10),
                display_name=random_string(10),
                bio=random_string(10),
                avatar_url=random_url())

def get_mock_post(author=None):
    if not author:
        author = get_mock_user().save()

    return Post(author=author,
                title=random_string(10),
                lead_paragraph=random_string(10),
                image_url=random_url(),
                content=random_string(10))

def get_mock_comment(author=None, post=None):
    if not author:
        author = get_mock_user().save()
    if not post:
        post = get_mock_post().save()

    return Comment(author=author,
                   post=post,
                   text=random_string(10))
