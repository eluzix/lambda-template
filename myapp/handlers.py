from myapp.http_utils import Response, request_handler


@request_handler()
def hello_world(request):
    res = Response()
    res.body = {'success': True, 'message': 'hello world'}

    return res

