from tests.test_utils import TestBase

class TestHome(TestBase):

    def test_404(self):
        response = self.client.get('/this/page/does/not/exist')
        assert response.status_code == 404

    def test_index(self):
        response = self.client.get('/')
        assert response.status_code == 200
