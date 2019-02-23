"""
Exports reusable helper functions.
"""

from functools import wraps

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import flash, redirect, request, session, url_for
from mistune import Markdown
from mongoengine.queryset.visitor import Q

from tiny.models import Comment, Post, User

markdown = Markdown(hard_wrap=True)

def sign_in_required(func):
    """
    Redirects to home page if not signed in. The user is passed on
    to the wrapped function if signed in.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            session.clear()
            return redirect(url_for('user.sign_in', next=request.url))
        kwargs['current_user'] = current_user
        return func(*args, **kwargs)
    return decorated_function

def sign_out_required(func):
    """
    Redirects to home page if already signed in.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if current_user:
            return redirect(url_for('home.index'))
        return func(*args, **kwargs)
    return decorated_function

def user_required(func):
    """
    Redirects to home page and notifies user if a selected user does not exist.
    The selected user (with email and password excluded) is passed on to the
    wrapped function if the user exists.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        selected_user = get_user(user_id=kwargs['user_id'], exclude=['email', 'password'])
        if not selected_user:
            flash('Oops - we couldn\'t find that user.', 'danger')
            return redirect(url_for('home.index'))
        kwargs['selected_user'] = selected_user
        return func(*args, **kwargs)
    return decorated_function

def post_required(func):
    """
    Redirects to home page and notifies user if a selected post does not exist.
    The selected post is passed on to the wrapped function if the post exists.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        selected_post = get_post(post_id=kwargs['post_id'])
        if not selected_post:
            flash('Oops - we couldn\'t find that post.', 'danger')
            return redirect(url_for('home.index'))
        kwargs['selected_post'] = selected_post
        return func(*args, **kwargs)
    return decorated_function

def author_required(func):
    """
    Takes in a selected post and the current user and determines if the current
    user is the author of the post. If not, the user is notified and redirected to
    the post view. The selected post and current user are passed to the wrapped
    function if they are the author.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        selected_post = kwargs['selected_post']
        current_user = kwargs['current_user']
        if selected_post.author.id != current_user.id:
            flash('Oops - you are not the author of this post.', 'danger')
            return redirect(url_for('post.show', post_id=kwargs['post_id']))
        return func(*args, **kwargs)
    return decorated_function

def to_ObjectId(value):
    """
    Safely converts value to ObjectId.
    """

    try:
        return ObjectId(value)
    except InvalidId:
        return ObjectId(None)

def get_user(user_id=None, email=None, exclude=[]):
    """
    Queries the database for a user.
    """

    return User.objects(Q(id=to_ObjectId(user_id)) | Q(email=email)) \
               .exclude(*exclude) \
               .first()

def get_current_user():
    """
    Returns the current user.
    """

    return get_user(session.get('user_id'))

def get_posts(user_id=None, exclude=[], order_by=[], skip=0, limit=12):
    """
    Queries the database for posts.
    """

    # cap number of posts to return
    limit = 100 if limit > 100 else limit

    # get posts by specific author
    if user_id:
        query_set = Post.objects(author=to_ObjectId(user_id))
    # get all posts
    else:
        query_set = Post.objects

    return query_set.exclude(*exclude) \
                    .order_by(*order_by) \
                    .skip(skip) \
                    .limit(limit)

def search_posts(search_text=None, exclude=[], order_by=[], skip=0, limit=12):
    """
    Performs a text search on posts.
    """

    if not search_text:
        return []

    # cap number of posts to return
    limit = 100 if limit > 100 else limit

    query_set = Post.objects.search_text(search_text)

    # need to ensure we have search text when ordering otherwise this will throw an error
    if search_text:
        query_set = query_set.order_by(*order_by)

    return query_set.exclude(*exclude) \
                    .skip(skip) \
                    .limit(limit)

def get_post(post_id=None, exclude=[]):
    """
    Returns a post.
    """

    return Post.objects(id=to_ObjectId(post_id)) \
               .exclude(*exclude) \
               .first()

def get_comments(user_id=None, post_id=None, exclude=[], order_by=[], skip=0, limit=12):
    """
    Returns comments on a post.
    """

    # cap number of comments to return
    limit = 100 if limit > 100 else limit

    return Comment.objects(Q(author=to_ObjectId(user_id)) | Q(post=to_ObjectId(post_id))) \
                  .exclude(*exclude) \
                  .order_by(*order_by) \
                  .skip(skip) \
                  .limit(limit)

def get_comment(comment_id=None, exclude=[]):
    """
    Returns a comment.
    """

    return Comment.objects(id=to_ObjectId(comment_id)) \
                  .exclude(*exclude) \
                  .first()

def serialize(results):
    """
    Serializes a group of results.
    """

    serialized = []
    for result in results:
        serialized.append(result.serialize())
    return serialized

def request_wants_json():
    """
    Returns if a request wants JSON.
    """

    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
           request.accept_mimetypes[best] > request.accept_mimetypes['text/html']

def markdown_to_html(value):
    """
    Converts markdown to HTML.
    """

    return markdown(value)
