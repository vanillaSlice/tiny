"""
Exports Tiny app data models.
"""

from mongoengine import (CASCADE,
                         DateTimeField,
                         Document,
                         EmailField,
                         ReferenceField,
                         StringField)

class User(Document):
    email = EmailField(unique=True)
    display_name = StringField()
    password = StringField()
    avatar_url = StringField()
    joined = DateTimeField()

    def serialize(self):
        return {
            "id": str(self.id),
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "joined": self.joined
        }

class Post(Document):
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    title = StringField()
    introduction = StringField()
    image_url = StringField()
    content = StringField()
    published = DateTimeField()

    def serialize(self):
        return {
            "id": str(self.id),
            "author": self.author.serialize(),
            "title": self.title,
            "introduction": self.introduction,
            "image_url": self.image_url,
            "published": self.published
        }

class Comment(Document):
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    post = ReferenceField(Post, reverse_delete_rule=CASCADE)
    content = StringField()
    published = DateTimeField()

    def serialize(self):
        return {
            "id": str(self.id),
            "author": self.author.serialize(),
            "post": self.post.serialize(),
            "content": self.content,
            "published": self.published
        }
