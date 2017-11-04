from mongoengine import (CASCADE,
                         DateTimeField,
                         Document,
                         EmailField,
                         ListField,
                         ReferenceField,
                         StringField)

class User(Document):
    email = EmailField(unique=True)
    display_name = StringField()
    password = StringField()
    avatar_url = StringField()
    joined = DateTimeField()

class Post(Document):
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    title = StringField()
    image_url = StringField()
    content = StringField()
    published = DateTimeField()
    edited = DateTimeField()
    tags = ListField(StringField())

class Comment(Document):
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    post = ReferenceField(Post, reverse_delete_rule=CASCADE)
    content = StringField()
    published = DateTimeField()
    edited = DateTimeField()
    likers = ListField(ReferenceField(User, reverse_delete_rule=CASCADE))
    dislikers = ListField(ReferenceField(User, reverse_delete_rule=CASCADE))
