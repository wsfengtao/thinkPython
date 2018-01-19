#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import ReturnDocument
import logging

__author__ = 'Geek_Feng'

logging.basicConfig(level=logging.INFO)

__all__ = ['StringField', 'BooleanField', 'IntegerField', 'DoubleField', 'DictField', 'Model']


# The mapping class
class _Field(object):
    def __init__(self, name, column_type, default):
        self.name = name
        self.column_type = column_type
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(_Field):
    def __init__(self, name=None, default=''):
        super().__init__(name, 'string', default)


class BooleanField(_Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', default)


class IntegerField(_Field):
    def __init__(self, name=None, default=0):
        super().__init__(name, 'integer', default)


class DoubleField(_Field):
    def __init__(self, name=None, default=0.0):
        super().__init__(name, 'double', default)


class DictField(_Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'dict', default)


# Metaclass for Model
class _ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        # exclude Model class itself
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)
        # Get the name of collection
        collectionname = attrs.get('__collection__', None) or name
        mappings = dict()
        fields = []
        # Get all fields of this db
        for k, v in attrs.items():
            if isinstance(v, _Field):
                mappings[k] = v
                fields.append(k)
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__database__'] = attrs.get('__database__', None)
        attrs['__mappings__'] = mappings  # The mapping relationship of attribute and field
        attrs['__collection__'] = collectionname
        attrs['__fields__'] = fields  # the name of attribute
        return type.__new__(mcs, name, bases, attrs)


# Model class
class Model(dict, metaclass=_ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    def find_one(cls, db, filter=None, *args, **kwargs):
        if filter is None:
            filter = {}
        res = db[cls.__database__][cls.__collection__].find_one(filter=filter, *args, **kwargs)
        if res:
            return res
        else:
            return None

    @classmethod
    def find_all(cls, db, *args, **kwargs):
        res = db[cls.__database__][cls.__collection__].find(*args, **kwargs)
        if res:
            return res
        else:
            return None

    @classmethod
    def delete_all(cls, db, filter=None, *args, **kwargs):
        if filter is None:
            filter = {}
        res = db[cls.__database__][cls.__collection__].delete_many(filter, *args, **kwargs)
        if res:
            return res
        else:
            return None

    @classmethod
    def update_one(cls, db, filter=None, update=None, *args, **kwargs):
        if filter is None:
            filter = {}
        if update is None:
            update = {}
        res = db[cls.__database__][cls.__collection__].update_one(filter, update, *args, **kwargs)
        if res:
            return res
        else:
            return None

    @classmethod
    def find_one_and_update(cls, db, filter=None, update=None, *args, **kwargs):
        if filter is None:
            filter = {}
        if update is None:
            update = {}
        res = db[cls.__database__][cls.__collection__].find_one_and_update(filter, update,
                                                                           return_document=ReturnDocument.AFTER, *args,
                                                                           **kwargs)
        if res:
            return res
        else:
            return None

    @classmethod
    def count(cls, db, filter=None, **kwargs):
        res = db[cls.__database__][cls.__collection__].count(filter, **kwargs)
        if res:
            return res
        else:
            return None

    def insert_one(self, db):
        document = {}
        for key in self.__fields__:
            document[key] = self.getValue(key)
        res = db[self.__database__][self.__collection__].insert_one(document)
        if res:
            return res.inserted_id
        else:
            return None
