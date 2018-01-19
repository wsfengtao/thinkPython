#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class EmailHandler(BaseHandler):
    __url__ = r"/api/v1/message/email"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.to_sen = self.streng_get_argument("to_sen", default=None,
                                               match=r'[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+')
        self.kemu = self.streng_get_argument("kemu", default=None, match='[1-4]')

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
            if self.to_sen and self.kemu:
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

    # POST :: 创建一封新邮件发送给指定收件人
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_message.send_email',
                                   args=[self.to_sen, self.kemu],
                                   queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
