import json
import logging
import time
from contextlib import contextmanager

import boto3

from myapp import app_config
from myapp.utils import ValueEncoder

_log = logging.getLogger(__name__)


class Logger(object):
    def __init__(self, stream_name=None) -> None:
        self.records = []
        self._client = None
        self._stream_name = False

        if stream_name is None:
            stream_name = 'stream_name'

        self._stream_name = stream_name

    def setup(self):
        if self._client is None:
            self._client = boto3.client('firehose')
            self._stream_name = app_config.get('firehose', {}).get(self._stream_name)

    def log(self, log_name, data, ts=None):
        if ts is None:
            ts = int(time.time())

        # data['log_id'] = str(utils.generate_id())
        data['ts'] = ts
        data['log_name'] = log_name

        self.records.append('{}\n'.format(json.dumps(data, cls=ValueEncoder)))

    def log_event(self, log_name, event, data):
        data['event'] = event
        self.log(log_name, data)

    def commit(self):
        if len(self.records) > 0:
            self.setup()

            if self._stream_name is None:
                for r in self.records:
                    _log.info('[Logger.commit] %s', r)
            else:
                try:
                    self._client.put_record_batch(
                        DeliveryStreamName=self._stream_name,
                        Records=[{'Data': d} for d in self.records]
                    )
                except Exception as e:
                    _log.error('Error committing logs to firehose, error: %s', e)

            self.records = []


app_logger = Logger()


@contextmanager
def logging_session(logger: Logger = None):
    if logger is None:
        logger = app_logger

    try:
        yield logger
    finally:
        logger.commit()


def add_request_info(request, data):
    try:
        data['ip'] = request.remote_ip
        data['request_id'] = request.request_id

        resource_path = request['requestContext'].get('resourcePath')
        if resource_path is not None:
            data['path'] = resource_path

    except Exception as e:
        # catch local app diff between lambda context
        pass

        user_agent = request.headers.get('User-Agent')
        if user_agent is not None:
            data['user_agent'] = user_agent

        header = request.headers.get('CloudFront-Is-Desktop-Viewer')
        if header is not None:
            data['is_desktop'] = header == 'true'

        header = request.headers.get('CloudFront-Is-Mobile-Viewer')
        if header is not None:
            data['is_mobile'] = header == 'true'

        header = request.headers.get('CloudFront-Is-Tablet-Viewer')
        if header is not None:
            data['is_tablet'] = header == 'true'

        country = request.headers.get('CloudFront-Viewer-Country')
        if country is not None:
            data['country'] = country.lower()

    return data
