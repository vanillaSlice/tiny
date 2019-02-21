import json
from unittest import mock

from tests.test_utils import get_mock_post, TestBase

class TestSearch(TestBase):

    def test_index(self):
        response = self.client.get('/search')
        assert response.status_code == 200

    def test_no_search_terms(self):
        response = self.client.get('/search?terms=', headers={'accept': 'application/json'})
        posts = json.loads(response.get_data(as_text=True))
        assert not posts
        assert response.status_code == 200

    @mock.patch('tiny.blueprints.search.search_posts')
    def test_search_success(self, mock_search_posts):
        term = 'python'

        # create posts containing search term
        mocked_posts = []
        for i in range(4):
            post = get_mock_post()
            post.content = term
            post.save()
            mocked_posts.append(post)

        mock_search_posts.return_value = mocked_posts

        # create other posts
        for i in range(6):
            get_mock_post().save()

        response = self.client.get('/search?terms={}'.format(term),
                                   headers={'accept': 'application/json'})
        assert response.status_code == 200

        # ensure only posts containing specified term are returned
        posts = json.loads(response.get_data(as_text=True))
        assert len(posts) == 4
