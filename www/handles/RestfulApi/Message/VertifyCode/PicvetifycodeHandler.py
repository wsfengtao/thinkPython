#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.web
import tornado.gen

__author__ = 'Geek_Feng'


class PicvetifycodeHandler(BaseHandler):
    __url__ = r"/api/v1/message/vertifycode/pic"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.picvetifycode = self.streng_get_argument("picvetifycode", default=None)
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
            if self.picvetifycode and self.pic_random_value:
                pass
            else:
                self.write({'code': 399, 'msg': 'missing get arguments!'})
                self.finish()
        elif self.request.method == 'POST':
            pass
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # GET :: 验证与传入手机号对应的图片验证码是否正确
    @tornado.gen.coroutine
    def get(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_message.vertify_pic_vertify_code',
                                   args=[self.picvetifycode, self.pic_random_value], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})

    # POST :: 生成随机验证码图片
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task,
                                   'www.celery_tasks.task_rest_message.generate_pic_vertify_code',
                                   args=[], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
