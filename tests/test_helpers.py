from unittest import TestCase

from tiny.helpers import is_int, is_valid_object_id

class HelpersTest(TestCase):
    def test_is_valid_object_id_false(self):
        self.assertFalse(is_valid_object_id("1"))

    def test_is_valid_object_id_true(self):
        self.assertTrue(is_valid_object_id("5a09bcdff3853517be67e293"))

    def test_is_int_false(self):
        self.assertFalse(is_int("hello"))

    def test_is_int_true(self):
        self.assertTrue(is_int(5))
