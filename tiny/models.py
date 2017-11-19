"""
Exports Tiny app data models.
"""
from datetime import datetime

from flask import url_for
from mongoengine import (CASCADE,
                         DateTimeField,
                         Document,
                         EmailField,
                         ReferenceField,
                         StringField,
                         URLField)

"""
Private helpers functions.
"""

def __delete_none__(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            __delete_none__(value)
    return d

def __default_avatar_img_path__():
    return url_for("static", filename="img/default-avatar.jpg", _external=True)

def __default_post_img_path__():
    return url_for("static", filename="img/default-post.jpg", _external=True)

"""
Model definitions.
"""

class User(Document):
    email = EmailField(unique=True, required=True)
    password = StringField(required=True)
    display_name = StringField(required=True, min_length=1, max_length=20)
    bio = StringField(max_length=160)
    avatar_url = URLField(required=True, default=__default_avatar_img_path__)
    created = DateTimeField(required=True, default=datetime.now)

    # for text search
    meta = {
        "indexes": [
            {
                "default_language": "english",
                "fields": ["$display_name"]
            }
        ]
    }

    def serialize(self):
        # we don't want to expose the user's email or password
        return __delete_none__({
            "id": str(self.id),
            "display_name": self.display_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "created": self.created
        })

class Post(Document):
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    title = StringField(required=True, min_length=1, max_length=100)
    preview = StringField(max_length=100)
    image_url = StringField(required=True, default=__default_post_img_path__)
    content = StringField(required=True, min_length=1, max_length=10_000)
    created = DateTimeField(required=True, default=datetime.now)
    last_updated = DateTimeField()

    # for text search
    meta = {
        "indexes": [
            {
                "default_language": "english",
                "fields": ["$title", "$preview", "$content", "$author"],
                "weights": {"title": 10, "preview": 5, "content": 2, "author": 1}
            }
        ]
    }

    def serialize(self):
        return __delete_none__({
            "id": str(self.id),
            "author": self.author.serialize() if self.author else None,
            "title": self.title,
            "preview": self.preview,
            "image_url": self.image_url,
            "content": self.content,
            "created": self.created,
            "last_updated": self.last_updated
        })

class Comment(Document):
    author = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    post = ReferenceField(Post, required=True, reverse_delete_rule=CASCADE)
    text = StringField(required=True, min_length=1, max_length=320)
    created = DateTimeField(required=True, default=datetime.now)

    def serialize(self):
        return __delete_none__({
            "id": str(self.id),
            "author": self.author.serialize() if self.author else None,
            "post": self.post.serialize() if self.post else None,
            "text": self.text,
            "created": self.created
        })
