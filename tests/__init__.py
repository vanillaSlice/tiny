import random
import string

from mongoengine import connect

import config
from tiny import create_app
from tiny.forms import (CommentForm,
                        PostForm,
                        SignInForm,
                        SignUpForm,
                        UpdatePasswordForm,
                        UpdateProfileForm)
from tiny.models import Comment, Post, User

def get_test_client():
    return create_app(testing=True).test_client()

def random_string(size):
    return "".join(random.choice(string.ascii_lowercase) for i in range(size))

def random_email():
    return "{}@{}.com".format(random_string(7), random_string(7))

def random_url():
    return "www.{}.com".format(random_string(7))

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
                preview=random_string(10),
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

def get_db_connection():
    return connect(host=config.Test.MONGODB_URI)

def clear_db():
    Comment.objects.delete()
    Post.objects.delete()
    User.objects.delete()

def get_mock_sign_up_data():
    password = random_string(7)
    return {"email": random_email(),
            "display_name": random_string(7),
            "password": password,
            "confirmation": password}

def get_mock_sign_up_form():
    data = get_mock_sign_up_data()
    return SignUpForm(email=data["email"],
                      display_name=data["display_name"],
                      password=data["password"],
                      confirmation=data["confirmation"])

def get_mock_sign_in_data():
    return {"email": random_email(),
            "password": random_string(7)}

def get_mock_sign_in_form():
    data = get_mock_sign_in_data()
    return SignInForm(email=data["email"],
                      password=data["password"])

def get_mock_update_profile_data():
    return {"display_name": random_string(7),
            "avatar_url": random_url(),
            "bio": random_string(7)}

def get_mock_update_profile_form():
    data = get_mock_update_profile_data()
    return UpdateProfileForm(display_name=data["display_name"],
                             avatar_url=data["avatar_url"],
                             bio=data["bio"])

def get_mock_update_password_data():
    new_password = random_string(7)
    return {"current_password": random_string(7),
            "new_password": new_password,
            "confirmation": new_password}

def get_mock_update_password_form():
    data = get_mock_update_password_data()
    return UpdatePasswordForm(current_password=data["current_password"],
                              new_password=data["new_password"],
                              confirmation=data["confirmation"])

def get_mock_post_data():
    return {"title": random_string(7),
            "preview": random_string(7),
            "image_url": random_url(),
            "content": random_string(7)}

def get_mock_post_form():
    data = get_mock_post_data()
    return PostForm(title=data["title"],
                    preview=data["preview"],
                    image_url=data["image_url"],
                    content=data["content"])

def get_mock_comment_data():
    return {"text": random_string(7)}

def get_mock_comment_form():
    data = get_mock_comment_data()
    return CommentForm(text=data["text"])
