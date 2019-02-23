"""
Exports post routes.
"""

from datetime import datetime

from flask import (Blueprint,
                   flash,
                   jsonify,
                   redirect,
                   render_template,
                   request,
                   session,
                   url_for)

from tiny.forms import CommentForm, PostForm
from tiny.helpers import (author_required,
                          get_comments,
                          get_posts,
                          markdown_to_html,
                          post_required,
                          serialize,
                          sign_in_required)
from tiny.models import Comment, Post

post = Blueprint('post', __name__, url_prefix='/post')

@post.route('/create', methods=['GET', 'POST'])
@sign_in_required
def create(current_user):
    """
    Create post route.
    """

    # parse the form
    form = PostForm(request.form, obj=Post())

    # render create post form if GET request
    if request.method == 'GET':
        return render_template('post/create.html', form=form)

    # render form again if submitted form is invalid
    if not form.validate_on_submit():
        return render_template('post/create.html', form=form), 400

    # create new post
    new_post = Post(author=current_user,
                    title=form.title.data,
                    lead_paragraph=form.lead_paragraph.data,
                    image_url=form.image_url.data,
                    content=form.content.data).save()

    # notify user
    flash('Post successfully created.', 'success')

    # redirect to post page
    return redirect(url_for('post.show', post_id=str(new_post.id)))

@post.route('/<post_id>/show', methods=['GET'])
@post_required
def show(post_id, selected_post):
    """
    Show post route.
    """

    return render_template('post/show.html',
                           form=CommentForm(),
                           post=selected_post,
                           is_author=str(selected_post.author.id) == session.get('user_id'))

@post.route('/<post_id>/settings', methods=['GET'])
@sign_in_required
@post_required
@author_required
def settings(current_user, post_id, selected_post):
    """
    Post settings route.
    """

    return render_template('post/settings.html', post=selected_post)

@post.route('/<post_id>/update', methods=['GET', 'POST'])
@sign_in_required
@post_required
@author_required
def update(current_user, post_id, selected_post):
    """
    Update post route.
    """

    # parse the form
    form = PostForm(request.form, obj=selected_post)

    # render update post form if GET request
    if request.method == 'GET':
        return render_template('post/update.html', form=form, post=selected_post)

    # render form again if submitted form is invalid
    if not form.validate_on_submit():
        return render_template('post/update.html', form=form, post=selected_post), 400

    # update the post information
    form.populate_obj(selected_post)
    selected_post.last_updated = datetime.now()
    selected_post.save()

    # notify the user
    flash('Post successfully updated.', 'success')

    # redirect back to post page
    return redirect(url_for('post.show', post_id=post_id))

@post.route('/<post_id>/delete', methods=['GET', 'POST'])
@sign_in_required
@post_required
@author_required
def delete(current_user, post_id, selected_post):
    """
    Delete post route.
    """

    # render delete page if GET request
    if request.method == 'GET':
        return render_template('post/delete.html', post=selected_post)

    selected_post.delete()

    # notify user
    flash('Successfully deleted post.', 'success')

    # redirect back to homepage
    return redirect(url_for('home.index'))

@post.route('/latest', methods=['GET'])
def latest():
    """
    Latest post route.
    """

    # get query parameters
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 12, type=int)

    # query for latest posts (making sure to exclude the actual content)
    results = get_posts(exclude=['content'],
                        order_by=['-created'],
                        skip=skip,
                        limit=limit)

    return jsonify(serialize(results))

@post.route('/<post_id>/comments', methods=['GET'])
@post_required
def comments(post_id, selected_post):
    """
    Post comments route.
    """

    # get query parameters
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 12, type=int)

    # query for post's comments (making sure to exclude the post itself)
    results = get_comments(post_id=post_id,
                           exclude=['post'],
                           order_by=['created'],
                           skip=skip,
                           limit=limit)

    return jsonify(serialize(results))

@post.route('/<post_id>/comment', methods=['POST'])
@sign_in_required
@post_required
def comment(current_user, post_id, selected_post):
    """
    Post comment route.
    """

    # parse the form
    form = CommentForm(request.form)

    # form is not valid so return error
    if not form.validate_on_submit():
        errors = []
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(error)
        return jsonify({'errors': errors, 'success': False}), 400

    # create the comment
    Comment(author=current_user,
            post=selected_post,
            text=form.text.data).save()

    return jsonify({'success': True}), 200

@post.route('/preview', methods=['POST'])
def preview():
    """
    Post preview route.
    """

    return jsonify({'html': markdown_to_html(request.form.get('content', ''))}), 200
