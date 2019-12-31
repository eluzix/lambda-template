import logging
import os

import yaml

from myapp import utils

_log = logging.getLogger(__name__)


class _AppConfig(dict):
    """Configuration object"""

    def __init__(self, **kwargs):
        super(_AppConfig, self).__init__(**kwargs)

        config_yml_file = os.path.join(os.path.dirname(__file__), '..', 'resources', 'config.yaml')

        with open(config_yml_file, 'r') as stream:
            try:
                config_yml = yaml.load(stream, Loader=yaml.FullLoader)
                utils.merge_dicts(self, config_yml)
            except yaml.YAMLError as exc:
                _log.error('Error loading default development env, error: %s', exc)

        self._stage = 'dev'

    def set_stage(self, val):
        self._stage = val

    def get_stage(self):
        return self._stage

    def get(self, key, default=None):
        """get a key relative to current `stage`"""
        return super(_AppConfig, self).get(self._stage, {}).get(key, default)

    def __getitem__(self, key):
        return super(_AppConfig, self).__getitem__(self._stage).__getitem__(key)


app_config = _AppConfig()
