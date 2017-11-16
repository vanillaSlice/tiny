from unittest import TestCase

from . import get_test_client

class TinyTest(TestCase):
    def setUp(self):
        self.app = get_test_client()

    def test_404(self):
        response = self.app.get("/this/page/does/not/exist")
        self.assertEqual(response.status_code, 404)
