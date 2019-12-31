import http.cookies
import json
import logging
import random
import urllib
from datetime import datetime
from functools import wraps
from urllib.parse import parse_qs, urlunparse

from myapp import app_config
from myapp import utils

_log = logging.getLogger(__name__)


class AuthError(Exception):
    pass


class Session(dict):
    def __init__(self, auto_initiate=True, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.loaded_from = None
        self.deleted = False

        if auto_initiate:
            self.session_id = utils.random_str(100)
            self._should_store = True
        else:
            self.session_id = None
            self._should_store = False

    def load_from_cookie_header(self, header):
        pass
        # if header is not None:
        #     cookie = http.cookies.SimpleCookie(header)
        #     cookie = cookie.get(app_config['session']['cookie.name'])
        #     if cookie is not None:
        #         session_id = cookie.value
        #         if session_id is not None and session_id.strip() != '':
        #             self.session_id = session_id.strip()
        #             self.load_by_id(self.session_id)
        #             self.loaded_from = 'cookie'

    def load_by_id(self, session_id):
        if session_id is None:
            return

        # data = ddb.get_item(app_config['tables']['sessions'], {'session_id': session_id})
        # if data is not None:
        #     now = int(time.time())
        #     if now - data['last_access'] <= app_config['session']['ttl']:
        #         self.update(json.loads(data['value']))
        #         self.session_id = session_id.strip()
        #         self.loaded_from = 'id'

    def store(self):
        pass
        # now = int(time.time())
        # item = {'session_id': self.session_id, 'last_access': now, 'value': json.dumps(self), 'expire_at': now + (60 * 60 * 6)}
        # ddb.put_item(app_config['tables']['sessions'], item)

    def clear(self):
        if self.session_id is not None:
            # ddb.delete_item(app_config['tables']['sessions'], {'session_id': self.session_id})
            self.deleted = True

    @property
    def id(self):
        return self.session_id

    def __setitem__(self, key, value):
        super(Session, self).__setitem__(key, value)
        self._should_store = True

    def should_store(self):
        # store session if we forced or on mod10
        return self._should_store or random.randint(10, 9999999) % 10 == 0


class Request(dict):
    def __init__(self, context, event):
        super(dict, self).__init__()
        self.context = context
        self.update(event)
        self._args = None
        self._form = None
        self._url = None
        self._session = None
        self.is_new_session = False
        self.user = None
        self.is_form_encoded = False

    @property
    def args(self):
        if self._args is None:
            self._args = self.get('queryStringParameters')
            if self._args is None:
                self._args = {}
        return self._args

    @property
    def form(self):
        if self._form is None:
            self._form = {}

            body = self.body
            if body is not None:
                content_type = self.headers.get('Content-Type')
                if content_type is None:
                    content_type = self.headers.get('content-type')

                if 'x-www-form-urlencoded' in content_type:
                    self.is_form_encoded = True
                    # body = parse_qs(body)
                    body = parse_qs(body.encode('ASCII'))
                    for k in body:
                        v = body[k]
                        try:
                            v = v.decode('utf-8')
                        except:
                            pass
                        if type(v) == list:
                            self._form[k] = v[0]
                elif 'json' in content_type:
                    self._form = json.loads(body)

        return self._form

    @property
    def body(self):
        return self.get('body')

    @property
    def headers(self):
        return self.get('headers', {})

    @property
    def stage(self):
        return self.get('requestContext', {}).get('stage', 'dev')

    @property
    def url(self):
        if self._url is None:
            schema = self.headers.get('X-Forwarded-Proto', 'https')
            netloc = self.headers['Host']
            path = self['path']
            params = ''
            query = '' if len(self.args) == 0 else urllib.parse.urlencode(self.args)
            fragment = ''
            self._url = urlunparse((schema, netloc, path, params, query, fragment))

        return self._url

    @property
    def method(self):
        return self.get('httpMethod')

    @property
    def remote_ip(self):
        return self['requestContext']['identity']['sourceIp']

    @property
    def request_id(self):
        return self['requestContext']['requestId']

    def session(self, auto_initiate=True):
        # if self._session is None:
        #     self._session = Session(auto_initiate=auto_initiate)
        #     self._session.load_from_cookie_header(self.headers.get('Cookie'))
        #
        #     if self._session.loaded_from is None:
        #         self._session.load_by_id(self.headers.get('x-map-auth'))

        return self._session


class Response(dict):
    def __init__(self, **kwargs):
        super(Response, self).__init__(**kwargs)

        # all ok by default... :)
        self['statusCode'] = 200

    @property
    def body(self):
        try:
            return json.loads(self.get('body', {}))
        except:
            return self.get('body')

    @body.setter
    def body(self, value):
        if isinstance(value, dict):
            self['body'] = json.dumps(value)
        else:
            self['body'] = value

    @property
    def headers(self):
        _headers = self.get('headers')
        if _headers is None:
            _headers = {}
            self['headers'] = _headers

        return _headers

    @property
    def status_code(self):
        return self['statusCode']

    @status_code.setter
    def status_code(self, code):
        self['statusCode'] = code


def request_handler(auth_required=False):
    def request_wrapper(f):
        @wraps(f)
        def catcher(event, context):
            request = Request(context, event)
            app_config.set_stage(request.stage)
            try:
                # if init_session or auth_required:
                #     session = request.session()
                #     uid = session.get('oid')
                #     if uid is not None:
                #         request.user = {'oid': uid}

                if auth_required and request.user is None:
                    raise AuthError()

                res = _make_response(request, f)

                if app_config.get('cookies.enabled'):
                    _set_cookie(request, res)

                return res

            except AuthError as ex:
                # session = request.session(auto_initiate=False)
                # if session is not None and session.id is not None:
                #     session.clear()
                return _make_error_response(401, ex, f, request=request)

            except Exception as ex:
                return _make_error_response(500, ex, f, request=request)

        return catcher

    return request_wrapper


# private methods
def _set_cookie(request, res):
    session = request.session(auto_initiate=False)
    if session is not None and session.id is not None:

        c = http.cookies.SimpleCookie()
        cookie_name = app_config['session']['cookie.name']
        c[cookie_name] = ''
        c[cookie_name]['domain'] = app_config['session']['cookie.domain']
        c[cookie_name]['path'] = '/'
        c[cookie_name]['secure'] = True

        if session.deleted:
            c[cookie_name]['expires'] = datetime.fromtimestamp(0).strftime('%a, %d %b %Y %H:%M:%S')
        else:
            if session.should_store():
                session.store()
            c[cookie_name] = session.id

        res.headers['Set-Cookie'] = c.output(header='').strip()


def _make_response(request, f):
    ret = f(request)
    # ret.headers['Access-Control-Allow-Credentials'] = True
    ret.headers['Access-Control-Allow-Origin'] = app_config['cors.domain']

    return ret


def _make_error_response(status_code, e, f, request=None, body=None):
    import traceback
    print(e)
    traceback.print_exc()

    res = Response()
    res.status_code = status_code

    if body is not None:
        res.body = body

    # res.headers['Access-Control-Allow-Credentials'] = True
    res.headers['Access-Control-Allow-Origin'] = app_config['cors.domain']

    return res
