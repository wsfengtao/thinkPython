#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class LoginHandler(BaseHandler):
    __url__ = r"/api/v1/users/login"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.login_type = self.streng_get_argument("login_type", default=None)
        self.password = self.streng_get_argument("password", default=None)
        self.tel_number = None
        self.email = None

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
            if self.login_type and self.password:
                if self.login_type == '1':
                    self.tel_number = self.streng_get_argument("account", default=None,
                                                               match=r'(^(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170'
                                                                     '[059]\d{7})$')
                    if self.tel_number:
                        pass
                    else:
                        self.write({'code': 400, 'msg': 'missing post arguments!'})
                        self.finish()
                elif self.login_type == '2':
                    self.email = self.streng_get_argument("account", default=None,
                                                          match=r'[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+')
                    if self.email:
                        pass
                    else:
                        self.write({'code': 400, 'msg': 'missing post arguments!'})
                        self.finish()
                else:
                    self.write({'code': 599, 'msg': "Not support this logging type!"})
                    self.finish()
            else:
                self.write({'code': 400, 'msg': 'missing post arguments!'})
                self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # POST :: 登陆
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_users.user_login',
                                   args=[self.login_type, self.tel_number, self.email, self.password], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
