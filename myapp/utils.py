import decimal
import enum
import json
import logging
import shutil
import string
import tempfile
from contextlib import contextmanager
from random import choice

# import requests

_log = logging.getLogger(__name__)


def random_str(size):
    letters_digits = string.ascii_letters + string.digits
    return ''.join([choice(letters_digits) for i in range(size)])


def random_digits(size):
    """
    return random number as string

    :type size: int
    :param size: number of digits in the number

    :rtype: str
    :return: the number
    """
    return ''.join([choice(string.digits) for i in range(size)])


def merge_dicts(a, b, path=None):
    """merges b into a"""
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


@contextmanager
def tmp_dir(cleanup=True):
    td = tempfile.mkdtemp()
    yield td
    if cleanup:
        shutil.rmtree(td, ignore_errors=True)


def append_if_exists(txt, lst):
    if txt is not None and txt != '':
        lst.append(txt)


def sanitize_ddb_obj(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = sanitize_ddb_obj(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = sanitize_ddb_obj(v)
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


def split_step(string, delim=',', step=2):
    tokens = string.split(delim)
    next_str = []
    ret = []
    for token in tokens:
        next_str.append(token.strip())
        if len(next_str) == step:
            ret.append(' '.join(next_str))
            next_str = []

    if len(next_str) > 0:
        ret.append(' '.join(next_str))

    return ret


class GrowingList(list):
    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([None] * (index + 1 - len(self)))
        list.__setitem__(self, index, value)


def decimal_to_number(val):
    if int(val) == val:
        return int(val)
    else:
        return float(val)


class ValueEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, enum.Enum):
            return o.value

        return super(ValueEncoder, self).default(o)
