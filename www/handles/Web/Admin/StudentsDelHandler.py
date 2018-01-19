#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class StudentsDelHandler(BaseHandler):
    __url__ = r"/admin/students/del\/?"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.deletestus = self.streng_get_argument('deletestus', default=None)

    @tornado.gen.coroutine
    def prepare(self):
        if self.request.method == 'GET':
            self.finish()
        elif self.request.method == 'POST':
            # 判定登录是否安全
            if self.current_user:
                now_user = self.current_user
                self.set_secure_cookie("user", now_user)
                if self.deletestus:
                    pass
                else:
                    self.finish()
            else:
                self.write({'code': 900, 'msg': 'please log in!'})
                self.finish()
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # POST :: 删除学员基本信息
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_web_admin.delete_student',
                                   args=[self.deletestus],
                                   queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
