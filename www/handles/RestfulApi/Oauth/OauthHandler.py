#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.gen
import tornado.web
from www.handles import BaseHandler

__author__ = 'Geek_Feng'


class OauthHandler(BaseHandler):
    __url__ = r'/api/v1/oauth'

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.grant_type = self.streng_get_argument("grant_type", default=None)
        self.app_secret = self.streng_get_argument("app_secret", default=None)

    @tornado.gen.coroutine
    def prepare(self):
        if self.request.method == 'GET':
            self.finish()
        elif self.request.method == 'POST':
            if self.grant_type == 'password' and self.app_secret:
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

    # POST :: 创建一个新的token并返回
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_oauth.generate_oauth_code',
                                   args=[self.app_secret], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
