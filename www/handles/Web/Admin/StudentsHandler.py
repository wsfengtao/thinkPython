#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www.handles import BaseHandler
import tornado.gen
import tornado.web

__author__ = 'Geek_Feng'


class StudentsHandler(BaseHandler):
    __url__ = r"/admin/students\/?"

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.nowpage = self.streng_get_argument("nowpage", default=None)
        self.apply_id = self.streng_get_argument("apply_id", default=None, match=r'\d{12,14}')
        self.username = self.streng_get_argument("username", default=None, match=r'[\u4E00-\u9FA5]{2,4}')
        self.identy_card_number = self.streng_get_argument("identy_card_number", default=None,
                                                           match=r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)')
        self.sexpicked = self.streng_get_argument("sexpicked", default=None)

    @tornado.gen.coroutine
    def prepare(self):
        if self.request.method == 'GET':
            # 判定登录是否安全
            if self.current_user:
                now_user = self.current_user
                self.set_secure_cookie("user", now_user)
                if self.nowpage:
                    try:
                        self.nowpage = int(self.nowpage)
                        pass
                    except Exception as e:
                        self.write(str(e))
                        self.finish()
                else:
                    self.finish()
            else:
                self.write({'code': 900, 'msg': 'please log in!'})
                self.finish()
        elif self.request.method == 'POST':
            # 判定登录是否安全
            if self.current_user:
                now_user = self.current_user
                self.set_secure_cookie("user", now_user)
                if self.apply_id and self.username and self.identy_card_number and self.sexpicked:
                    pass
                else:
                    self.finish()
            else:
                self.redirect("/admin/login")
        elif self.request.method == 'PUT':
            self.finish()
        elif self.request.method == 'PATCH':
            self.finish()
        elif self.request.method == 'DELETE':
            self.finish()

    # GET :: 获取当前页学生信息
    @tornado.gen.coroutine
    def get(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_web_admin.get_page_student',
                                   args=[self.nowpage], queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})

    # POST :: 新增学员信息
    @tornado.gen.coroutine
    def post(self):
        r = yield tornado.gen.Task(self.celery.send_task, 'www.celery_tasks.task_web_admin.add_new_student',
                                   args=[self.apply_id, self.username, self.identy_card_number, self.sexpicked],
                                   queue='queue1')
        if r.state == 'SUCCESS':
            self.write(r.result)
        else:
            self.write({'code': 888, 'msg': 'the server has problems!'})
