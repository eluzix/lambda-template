import json
import unittest

from apptests import BaseTestCase
from myapp import handlers


class SqsTestCase(BaseTestCase):
    def test_sqs_handler(self):
        event = {'Records': [{'body': json.dumps({'test': 'value'})}]}
        handlers.sqs_handler(event, None)

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
