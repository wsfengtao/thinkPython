#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.gen
import tornado.web
from www.handles import BaseHandler

__author__ = 'Geek_Feng'


class SmsvetifycodeHandler(BaseHandler):
    __url__ = r"/api/v1/message/vertifycode/sms"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.picvetifycode = self.streng_get_argument("picvetifycode", default=None)
        self.tel_number = self.streng_get_argument("tel_number", default=None)
        self.pic_random_value = self.streng_get_argument("pic_random_value", default=None)

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
            if self.picvetifycode and self.pic_random_value and self.tel_number:
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

    # POST :: 生成短信验证码并发送
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task,
                                   'www.celery_tasks.task_rest_message.generate_and_send_sms_vertify_code',
                                   args=[self.picvetifycode, self.pic_random_value, self.tel_number], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
