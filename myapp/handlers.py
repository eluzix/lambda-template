import json
import os
import sys
sys.path.append('vendors')

from myapp import app_config
from myapp.http_utils import Response, request_handler


@request_handler()
def hello_world(request):
    qs_arg = request.args.get('test_qs_arg')

    # value_from_json_body = request['form']['json_key']

    res = Response()
    res.body = {'success': True, 'message': 'hello world'}

    return res


def sqs_handler(event, context):
    # set current stage manually (like request_handler)
    stage = os.environ.get('APP_STAGE')
    if stage is not None:
        app_config.set_stage(stage)

    for record in event['Records']:
        data = json.loads(record["body"])
        print(data)

