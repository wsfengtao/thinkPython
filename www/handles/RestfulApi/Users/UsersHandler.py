#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class UsersHandler(BaseHandler):
    __url__ = r"/api/v1/users"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.apply_id = self.streng_get_argument("apply_id", default=None)
        self.smsvetifycode = self.streng_get_argument("smsvetifycode", default=None)
        self.tel_number = self.streng_get_argument("tel_number", default=None,
                                                   match=r'(^(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7})$')
        self.email = self.streng_get_argument("email", default=None,
                                              match=r'[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+')
        self.password = self.streng_get_argument("password", default=None)
        self.new_password = self.streng_get_argument("new_password", default=None)

    @tornado.gen.coroutine
    def prepare(self):
        # 校验是否含有token并且有效
        if self.check_token_security():
            pass
        else:
            self.finish()
            return
        if self.request.method == 'GET':
            if self.tel_number and self.password:
                pass
            else:
                self.write({'code': 399, 'msg': 'missing get arguments!'})
                self.finish()
        elif self.request.method == 'POST':
            if self.smsvetifycode and self.tel_number and self.password and self.email and self.apply_id:
                pass
            else:
                self.write({'code': 400, 'msg': 'missing post arguments!'})
                self.finish()
        elif self.request.method == 'PUT':
            if self.new_password and self.password and self.tel_number and self.smsvetifycode:
                pass
            else:
                self.write({'code': 398, 'msg': 'missing put arguments!'})
                self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # GET :: 获取指定号码用户的所有信息
    @tornado.gen.coroutine
    def get(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_users.get_user_information',
                                   args=[self.tel_number, self.password], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})

    # POST :: 注册一个新的用户并返回是否成功信息
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_users.register_new_user',
                                   args=[self.smsvetifycode, self.tel_number, self.password, self.email, self.apply_id],
                                   queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})

    # PUT :: 更新用户的信息(目前只支持更新原始登陆方式的密码)
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_rest_users.update_user_information',
                                   args=[self.smsvetifycode, self.tel_number, self.password, self.new_password],
                                   queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
