#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class LogoutHandler(BaseHandler):
    __url__ = r"/api/v1/users/logout"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.tel_number = self.streng_get_argument("tel_number", default=None)
        self.password = self.streng_get_argument("password", default=None)

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
            if self.tel_number and self.password:
                pass
            else:
                self.write({'code': 400, 'msg': 'missing post arguments!'})
                self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # POST :: 注销当前用户
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_users.user_logout',
                                   args=[self.tel_number, self.password],
                                   queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
