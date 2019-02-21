import json

from tests.test_utils import get_mock_comment, get_mock_post, random_string, random_url, sign_out, TestBase
from tiny.models import Comment, Post

class TestPost(TestBase):

    #
    # Create tests.
    #

    def get_mock_post_data(self):
        return {'title': random_string(10),
                'lead_paragraph': random_string(10),
                'image_url': random_url(),
                'content': random_string(10)}

    def assert_create_successful(self, data):
        response = self.client.post('/post/create', data=data)
        post = Post.objects.first()
        assert post.author.id == self.user.id
        assert post.title == data['title']
        assert post.lead_paragraph == data['lead_paragraph']
        assert post.image_url == data['image_url']
        assert post.content == data['content']
        assert post.created is not None
        assert post.last_updated is None

    def assert_create_unsuccessful(self, data):
        response = self.client.post('/post/create', data=data)
        assert Post.objects.count() == 0
        assert response.status_code == 400

    def test_create_sign_in_required(self):
        sign_out(self.client)
        response = self.client.post('/post/create')
        assert response.status_code == 302

    def test_create_GET(self):
        response = self.client.get('/post/create')
        assert response.status_code == 200

    def test_create_no_title(self):
        data = self.get_mock_post_data()
        data['title'] = ''
        self.assert_create_unsuccessful(data=data)

    def test_create_title_too_long(self):
        data = self.get_mock_post_data()
        data['title'] = random_string(161)
        self.assert_create_unsuccessful(data=data)

    def test_create_title_length_equal_to_minimum(self):
        data = self.get_mock_post_data()
        data['title'] = random_string(1)
        self.assert_create_successful(data=data)

    def test_create_title_length_equal_to_maximum(self):
        data = self.get_mock_post_data()
        data['title'] = random_string(160)
        self.assert_create_successful(data=data)

    def test_create_lead_paragraph_too_long(self):
        data = self.get_mock_post_data()
        data['lead_paragraph'] = random_string(501)
        self.assert_create_unsuccessful(data=data)

    def test_create_lead_paragraph_length_equal_to_maximum(self):
        data = self.get_mock_post_data()
        data['lead_paragraph'] = random_string(500)
        self.assert_create_successful(data=data)

    def test_create_no_image_url(self):
        data = self.get_mock_post_data()
        data['image_url'] = ''
        self.assert_create_unsuccessful(data=data)

    def test_create_invalid_image_url(self):
        data = self.get_mock_post_data()
        data['image_url'] = 'invalid'
        self.assert_create_unsuccessful(data=data)

    def test_create_no_content(self):
        data = self.get_mock_post_data()
        data['content'] = ''
        self.assert_create_unsuccessful(data=data)

    def test_create_content_too_long(self):
        data = self.get_mock_post_data()
        data['content'] = random_string(10_001)
        self.assert_create_unsuccessful(data=data)

    def test_create_content_length_equal_to_minimum(self):
        data = self.get_mock_post_data()
        data['content'] = random_string(1)
        self.assert_create_successful(data=data)

    def test_create_content_length_equal_to_maximum(self):
        data = self.get_mock_post_data()
        data['content'] = random_string(10_000)
        self.assert_create_successful(data=data)

    def test_create_success(self):
        data = self.get_mock_post_data()
        self.assert_create_successful(data=data)

    #
    # Show tests.
    #

    def test_show_invalid_id(self):
        response = self.client.get('/post/1/show')
        assert response.status_code == 302

    def test_show_no_post_with_id(self):
        response = self.client.get('/post/5a09bcdff3853517be67e293/show')
        assert response.status_code == 302

    def test_show_success(self):
        post = get_mock_post().save()
        response = self.client.get('/post/{}/show'.format(str(post.id)))
        assert response.status_code == 200

    #
    # Settings tests.
    #

    def test_settings_sign_in_required(self):
        sign_out(self.client)
        post = get_mock_post(author=self.user).save()
        response = self.client.get('/post/{}/settings'.format(str(post.id)))
        assert response.status_code == 302

    def test_settings_invalid_id(self):
        response = self.client.get('/post/1/settings')
        assert response.status_code == 302

    def test_settings_no_post_with_id(self):
        response = self.client.get('/post/5a09bcdff3853517be67e293/settings')
        assert response.status_code == 302

    def test_settings_not_the_author(self):
        post = get_mock_post().save()
        response = self.client.get('/post/{}/settings'.format(str(post.id)))
        assert response.status_code == 302

    def test_settings_success(self):
        post = get_mock_post(author=self.user).save()
        response = self.client.get('/post/{}/settings'.format(str(post.id)))
        assert response.status_code == 200

    #
    # Update tests.
    #

    def assert_update_successful(self, post_id, data):
        response = self.client.post('/post/{}/update'.format(post_id), data=data)
        post = Post.objects(id=post_id).first()
        assert post.title == data['title']
        assert post.lead_paragraph == data['lead_paragraph']
        assert post.image_url == data['image_url']
        assert post.content == data['content']
        assert post.created is not None
        assert post.last_updated is not None
        assert response.status_code == 302

    def assert_update_unsuccessful(self, post_id, data):
        response = self.client.post('/post/{}/update'.format(post_id), data=data)
        assert response.status_code == 400

    def test_update_sign_in_required(self):
        sign_out(self.client)
        post = get_mock_post(author=self.user).save()
        response = self.client.get('/post/{}/update'.format(str(post.id)))
        assert response.status_code == 302

    def test_update_invalid_id(self):
        response = self.client.get('/post/1/update')
        assert response.status_code == 302

    def test_update_no_post_with_id(self):
        response = self.client.get('/post/5a09bcdff3853517be67e293/update')
        assert response.status_code == 302

    def test_update_not_the_author(self):
        post = get_mock_post().save()
        response = self.client.get('/post/{}/update'.format(str(post.id)))
        assert response.status_code == 302

    def test_update_GET(self):
        post = get_mock_post(author=self.user).save()
        response = self.client.get('/post/{}/update'.format(str(post.id)))
        assert response.status_code == 200

    def test_update_no_title(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['title'] = ''
        self.assert_update_unsuccessful(str(post.id), data)

    def test_update_title_too_long(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['title'] = random_string(161)
        self.assert_update_unsuccessful(str(post.id), data)

    def test_update_title_length_equal_to_minimum(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['title'] = random_string(1)
        self.assert_update_successful(str(post.id), data)

    def test_update_title_length_equal_to_maximum(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['title'] = random_string(16)
        self.assert_update_successful(str(post.id), data)

    def test_update_lead_paragraph_too_long(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['lead_paragraph'] = random_string(501)
        self.assert_update_unsuccessful(str(post.id), data)

    def test_update_lead_paragraph_length_equal_to_maximum(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['lead_paragraph'] = random_string(500)
        self.assert_update_successful(str(post.id), data)

    def test_update_no_image_url(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['image_url'] = ''
        self.assert_update_unsuccessful(str(post.id), data)

    def test_update_invalid_image_url(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['image_url'] = 'invalid'
        self.assert_update_unsuccessful(str(post.id), data)

    def test_update_no_content(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['content'] = ''
        self.assert_update_unsuccessful(str(post.id), data)

    def test_update_content_too_long(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['content'] = random_string(10_001)
        self.assert_update_unsuccessful(str(post.id), data)

    def test_create_content_length_equal_to_minimum(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['content'] = random_string(1)
        self.assert_update_successful(str(post.id), data)

    def test_create_content_length_equal_to_maximum(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        data['content'] = random_string(10_000)
        self.assert_update_successful(str(post.id), data)

    def test_update_success(self):
        post = get_mock_post(author=self.user).save()
        data = self.get_mock_post_data()
        self.assert_update_successful(str(post.id), data)

    #
    # Delete tests.
    #

    def test_delete_sign_in_required(self):
        sign_out(self.client)
        post = get_mock_post(author=self.user).save()
        response = self.client.get('/post/{}/delete'.format(str(post.id)))
        assert response.status_code == 302

    def test_delete_invalid_id(self):
        response = self.client.get('/post/1/delete')
        assert response.status_code == 302

    def test_delete_no_post_with_id(self):
        response = self.client.get('/post/5a09bcdff3853517be67e293/delete')
        assert response.status_code == 302

    def test_delete_not_the_author(self):
        post = get_mock_post().save()
        response = self.client.get('/post/{}/delete'.format(str(post.id)))
        assert response.status_code == 302

    def test_delete_GET(self):
        post = get_mock_post(author=self.user).save()
        response = self.client.get('/post/{}/delete'.format(str(post.id)))
        assert response.status_code == 200

    def test_delete_success(self):
        post = get_mock_post(author=self.user).save()
        response = self.client.post('/post/{}/delete'.format(str(post.id)))
        assert Post.objects(id=post.id).first() is None
        assert response.status_code == 302

    #
    # Latest tests.
    #

    def test_latest_success(self):
        # create posts
        for i in range(16):
            get_mock_post().save()

        # assert that we get first page of results
        response = self.client.get('/post/latest?limit=10&skip=0')

        posts = json.loads(response.get_data(as_text=True))
        assert len(posts) == 10

        assert response.status_code == 200

        # assert that we get the second page of results
        response = self.client.get('/post/latest?limit=10&skip=10')

        posts = json.loads(response.get_data(as_text=True))
        assert len(posts) == 6

        assert response.status_code == 200

    #
    # Get comments tests.
    #

    def test_get_comments_invalid_id(self):
        response = self.client.get('/post/1/comments')
        assert response.status_code == 302

    def test_get_comments_no_post_with_id(self):
        response = self.client.get('/post/5a09bcdff3853517be67e293/comments')
        assert response.status_code == 302

    def test_get_comments_success(self):
        # create post and comments
        post = get_mock_post().save()
        for i in range(4):
            get_mock_comment(post=post).save()

        # create another post and comments
        another_post = get_mock_post().save()
        for i in range(6):
            get_mock_comment(post=another_post).save()

        response = self.client.get('/post/{}/comments'.format(str(post.id)))

        # ensure only comments for specified post are returned
        comments = json.loads(response.get_data(as_text=True))
        assert len(comments) == 4

        assert response.status_code == 200

    #
    # Create comment tests.
    #

    def assert_create_comment_successful(self, post, data):
        response = self.client.post('/post/{}/comment'.format(str(post.id)), data=data)
        comment = Comment.objects(post=post.id).first()
        assert comment.author == self.user
        assert comment.post == post
        assert comment.text == data['text']
        assert comment.created is not None
        assert response.status_code == 200

    def assert_create_comment_unsuccessful(self, post, data):
        response = self.client.post('/post/{}/comment'.format(str(post.id)), data=data)
        assert response.status_code == 400

    def get_mock_comment_data(self):
        return {'text': random_string(10)}

    def test_create_comment_sign_in_required(self):
        sign_out(self.client)
        data = self.get_mock_comment_data()
        response = self.client.post('/post/5a09bcdff3853517be67e293/comment', data=data)
        assert response.status_code == 302

    def test_create_comment_invalid_id(self):
        data = self.get_mock_comment_data()
        response = self.client.post('/post/1/comment', data=data)
        assert response.status_code == 302

    def test_create_comment_no_post_with_id(self):
        data = self.get_mock_comment_data()
        response = self.client.post('/post/5a09bcdff3853517be67e293/comment', data=data)
        assert response.status_code == 302

    def test_create_comment_no_text(self):
        post = get_mock_post().save()
        data = self.get_mock_comment_data()
        data['text'] = ''
        self.assert_create_comment_unsuccessful(post, data)

    def test_create_comment_text_too_long(self):
        post = get_mock_post().save()
        data = self.get_mock_comment_data()
        data['text'] = random_string(501)
        self.assert_create_comment_unsuccessful(post, data)

    def test_create_comment_text_length_equal_to_minimum(self):
        post = get_mock_post().save()
        data = {'text': random_string(1)}
        self.assert_create_comment_successful(post, data)

    def test_create_comment_text_length_equal_to_maximum(self):
        post = get_mock_post().save()
        data = {'text': random_string(500)}
        self.assert_create_comment_successful(post, data)

    def test_create_comment_success(self):
        post = get_mock_post().save()
        data = {'text': random_string(7)}
        self.assert_create_comment_successful(post, data)

    #
    # Preview tests.
    #

    def test_preview_no_content(self):
        response = self.client.post('/post/preview', data={})
        html = json.loads(response.get_data(as_text=True))['html']
        assert html == ''
        assert response.status_code == 200

    def test_preview_success(self):
        response = self.client.post('/post/preview', data={'content': '# Hello'})
        html = json.loads(response.get_data(as_text=True))['html']
        assert html == '<h1>Hello</h1>\n'
        assert response.status_code == 200
