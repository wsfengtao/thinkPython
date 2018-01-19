#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class HomeHandler(BaseHandler):
    __url__ = r"/"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @tornado.gen.coroutine
    def prepare(self):
        if self.request.method == 'GET':
            pass
        elif self.request.method == 'POST':
            self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # GET :: 登陆官方首页
    @tornado.gen.coroutine
    def get(self):
        self.render("jieshao_index.html")
