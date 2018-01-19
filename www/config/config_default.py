#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform

__author__ = 'Geek_Feng'

configs_default = {
    'db': {  # Database configuration information
        'type': 'mongodb',
        'db_settings': {
            'port': 27017,
            'host': '127.0.0.1'
        }
    },
    'app': {  # Application configuration information
        'port': 8888,
        'settings': {
            'cookie_secret': 'pke39cnk2f9aj2nlf9cj2n44qp',
            'xsrf_cookies': False,
            'debug': False if platform.system() == 'Linux' else True
        }
    },
    'tcp': {
        'port': 8889,
        'address': '0.0.0.0'
    }
}


class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def toDict(d):
    D = Dict()
    for k, v in d.items():
        if isinstance(v, dict):
            D[k] = toDict(v)
        else:
            D[k] = v
    return D


configs = toDict(configs_default)
