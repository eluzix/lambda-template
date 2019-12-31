import unittest

from apptests import BaseTestCase
from myapp import utils


class TestUtilsCase(BaseTestCase):
    def test_random_str(self):
        s1 = utils.random_digits(10)
        s2 = utils.random_digits(10)
        self.assertEqual(len(s1), 10)
        self.assertEqual(len(s2), 10)
        self.assertNotEqual(s1, s2)


if __name__ == '__main__':
    unittest.main()
