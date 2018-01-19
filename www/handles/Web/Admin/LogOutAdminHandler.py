#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class LogOutAdminHandler(BaseHandler):
    __url__ = r"/admin/logout\/?"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @tornado.gen.coroutine
    def prepare(self):
        if self.request.method == 'GET':
            self.finish()
        elif self.request.method == 'POST':
            # 判定登录是否安全
            if self.current_user:
                pass
            else:
                self.redirect("/admin/login")
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # POST :: 注销操作
    @tornado.gen.coroutine
    def post(self):
        self.clear_cookie("user")
        self.write({'code': 200, 'msg': 'logout success!'})
