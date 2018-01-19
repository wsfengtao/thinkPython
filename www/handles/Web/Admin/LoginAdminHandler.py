#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class LoginAdminHandler(BaseHandler):
    __url__ = r"/admin\/?"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.zhanghu = self.streng_get_argument("zhanghu", default=None)
        self.password = self.streng_get_argument("password", default=None)

    @tornado.gen.coroutine
    def prepare(self):
        if self.request.method == 'GET':
            pass
        elif self.request.method == 'POST':
            if self.zhanghu and self.password:
                pass
            else:
                self.write({'code': 501, 'msg': "account and password can't be empty!"})
                self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # GET :: 后台登陆页
    @tornado.gen.coroutine
    def get(self):
        self.render("index.html")

    # POST :: 登陆操作
    @tornado.gen.coroutine
    def post(self):
        if self.zhanghu == 'admin@123456' and self.password == '123456':
            self.set_secure_cookie("user", self.zhanghu)
            self.write({'code': 200, 'msg': 'login success!'})
        else:
            self.write({'code': 500, 'msg': 'account or password is not correct!'})
