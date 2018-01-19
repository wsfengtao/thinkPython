#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.gen
import tornado.web
from www.handles import BaseHandler

__author__ = 'Geek_Feng'


class GetQsSizeHandler(BaseHandler):
    __url__ = r'/api/v1/tiku/size'

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.city = self.streng_get_argument("city", match=r'^[a-z]+$')
        self.cycle_type = self.streng_get_argument("cycle_type",
                                                   match=r'^([c]{1}[1-5]{1}$)|([a]{1}[1-3]{1}$)|([b]{1}[1,2]{1}$)|'
                                                         r'([b]{1}[1,2]{1}$)|([d,e,f,p,n]{1}$)')
        self.kemu_type = self.streng_get_argument("kemu_type", match=r'^[1-4]{1}$')
        self.zhangjie = self.streng_get_argument("zhangjie", match=r'^[1-9]\d{0,1}$')
        self.callback = self.streng_get_argument("callback")

    @tornado.gen.coroutine
    def prepare(self):
        # 校验是否含有token并且有效
        if self.check_token_security(is_jsonp=True, callback=self.callback):
            pass
        else:
            self.finish()
            return
        if self.request.method == 'GET':
            if self.city and self.cycle_type and self.kemu_type and self.zhangjie and self.callback:
                pass
            else:
                self.write_jsonp(self.callback, {'code': 399, 'msg': 'missing get arguments!'})
                self.finish()
        elif self.request.method == 'POST':
            self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # POST :: 获取某套题库的size
    @tornado.gen.coroutine
    def get(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_tiku.get_qs_size',
                                   args=[self.city, self.cycle_type, self.kemu_type, self.zhangjie], queue='queue1')
        if r.state == 'SUCCESS':
            self.write_jsonp(self.callback, r.result)
        else:
            self.write_jsonp(self.callback, {'code': 888, 'msg': 'the server has problems!'})
