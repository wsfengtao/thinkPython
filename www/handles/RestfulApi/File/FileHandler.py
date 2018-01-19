#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class FileHandler(BaseHandler):
    __url__ = r"/api/v1/file"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @tornado.gen.coroutine
    def prepare(self):
        # 校验是否含有token并且有效
        if self.check_token_security():
            pass
        else:
            self.finish()
            return
        if self.request.method == 'GET':
            self.finish()
        elif self.request.method == 'POST':
            self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()
