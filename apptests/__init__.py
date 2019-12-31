import json
import logging
import unittest

import boto3

from myapp import app_config


class DummyRequest(object):
    def __init__(self):
        self.user = {}
        self.form = {}
        self.args = {}


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        app_config.set_stage('unittest')
        boto3.setup_default_session(profile_name='profile')


class RequestTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.context = {}

    @staticmethod
    def build_request(method='POST', path='/cant/bother/with', body='', content_type='application/x-www-form-urlencoded; charset=utf-8'):
        return {
            "body": body,
            "httpMethod": method,
            "resource": path,
            "queryStringParameters": {},
            "requestContext": {
                "httpMethod": method,
                "requestId": "2100b73e-d59f-11e6-bf13-a34470b2f028",
                "resourceId": "f0ur9r",
                "apiId": "y9hvb1ii28",
                "stage": "unittest",
                "resourcePath": path,
                "identity": {
                    "apiKey": None,
                    "userArn": None,
                    "user": None,
                    "cognitoIdentityPoolId": None,
                    "userAgent": "MyApp/1.0 (com.myapp.client; build:1; iOS 10.0.2) Alamofire/4.2.0",
                    "accountId": None,
                    "cognitoAuthenticationType": None,
                    "accessKey": None,
                    "caller": None,
                    "cognitoIdentityId": None,
                    "sourceIp": "82.81.86.82",
                    "cognitoAuthenticationProvider": None
                },
                "accountId": "394154862727"
            },
            "headers": {
                "Via": "1.1 7b722dfff4eb2db46dc0c2a7d78b5ea9.cloudfront.net (CloudFront)",
                "Accept-Language": "en-US;q=1.0, he-US;q=0.9, es-US;q=0.8, de-US;q=0.7, ja-US;q=0.6",
                "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
                "CloudFront-Is-SmartTV-Viewer": "false",
                "CloudFront-Forwarded-Proto": "https",
                "CloudFront-Is-Mobile-Viewer": "false",
                "X-Forwarded-For": "82.81.86.82, 54.239.183.71",
                "CloudFront-Viewer-Country": "IL",
                "Accept": "*/*",
                "User-Agent": "MyApp/1.0 (com.myapp.client; build:1; iOS 10.0.2) Alamofire/4.2.0",
                "Host": "y9hvb1ii28.execute-api.us-east-1.amazonaws.com",
                "X-Forwarded-Proto": "https",
                "X-Amz-Cf-Id": "k_Q4JD5YpY0nIXeiiuZA2oNdc3qnDQ4PLPs1ZlMLmboZmXgZn4Wtgw==",
                "CloudFront-Is-Tablet-Viewer": "false",
                "X-Forwarded-Port": "443",
                "Content-Type": content_type,
                # "Authorization": "OAuth oauth_signature=\"5jcRl1%2FHZYdaLRZj6AnmF43dwbk%3D\", oauth_signature_method=\"HMAC-SHA1\", oauth_nonce=\"C729AA44-8808-46BF-9628-8AB61BF25CB5\", oauth_version=\"1.0\", oauth_timestamp=\"1483879010\", oauth_consumer_key=\"jNf528NQnSEDnBajPJWR\"",
                "CloudFront-Is-Desktop-Viewer": "true"
            },
            "stageVariables": None,
            "path": path,
            "pathParameters": None,
            "isBase64Encoded": False
        }

    @staticmethod
    def build_json_request(body, **kwargs):
        return RequestTestCase.build_request(body=json.dumps(body), content_type='application/json; charset=utf-8', **kwargs)
