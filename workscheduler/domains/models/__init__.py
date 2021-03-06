# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base


OrmBase = declarative_base()


@staticmethod
def validate(obj, key, value):
    if not value:
        raise AssertionError('no {} provided'.format(key))
    t = getattr(obj, key).type
    if hasattr(t, 'length'):
        length = t.length
        if length and len(value) > length:
            raise AssertionError('{} is less than {}'.format(key, length))
    return value


OrmBase.validate = validate
