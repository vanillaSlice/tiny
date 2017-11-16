"""
Exports Tiny app data models.
"""

from datetime import datetime

from mongoengine import (CASCADE,
                         DateTimeField,
                         Document,
                         EmailField,
                         ReferenceField,
                         StringField)

from tiny.helpers import del_none

class User(Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    display_name = StringField(required=True, min_length=1, max_length=20)
    bio = StringField(max_length=160)
    avatar_url = StringField(required=True, default="/static/img/default-avatar.jpg")
    created = DateTimeField(required=True, default=datetime.now)

    # for text search
    meta = {
        "indexes": [
            {
                "fields": ["$display_name"]
            }
        ]
    }

    def serialize(self):
        # we don't want to expose the user's email or password
        return del_none({
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
    image_url = StringField(required=True, default="/static/img/default-post.jpg")
    content = StringField(required=True, min_length=1, max_length=10_000)
    created = DateTimeField(required=True, default=datetime.now)
    last_updated = DateTimeField()

    # for text search
    meta = {
        "indexes": [
            {
                "default_language": "english",
                "fields": ["$author", "$title", "$preview", "$content"],
                "weights": {"title": 10, "preview": 5, "content": 2, "author": 1}
            }
        ]
    }

    def serialize(self):
        return del_none({
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
        return del_none({
            "id": str(self.id),
            "author": self.author.serialize() if self.author else None,
            "post": self.post.serialize() if self.post else None,
            "text": self.text,
            "created": self.created
        })
