"""
Contains app models.
"""

from mongoengine import (CASCADE,
                         DateTimeField,
                         Document,
                         EmailField,
                         ListField,
                         ReferenceField,
                         StringField)

class User(Document):
    """
    User model.
    """
    email = EmailField(unique=True)
    display_name = StringField()
    password = StringField()
    avatar_url = StringField()
    joined = DateTimeField()

class Post(Document):
    """
    Post model.
    """
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    title = StringField()
    image_url = StringField()
    content = StringField()
    published = DateTimeField()
    edited = DateTimeField()
    tags = ListField(StringField())

class Comment(Document):
    """
    Comment model.
    """
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    post = ReferenceField(Post, reverse_delete_rule=CASCADE)
    content = StringField()
    published = DateTimeField()
    edited = DateTimeField()
    likers = ListField(ReferenceField(User, reverse_delete_rule=CASCADE))
    dislikers = ListField(ReferenceField(User, reverse_delete_rule=CASCADE))
