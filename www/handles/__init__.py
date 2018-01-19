#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
import json
import re
from ..vender import verify_token

__author__ = 'Geek_Feng'


class BaseHandler(tornado.web.RequestHandler):
    """web request 基类 用于定义通用操作
        1.  在此处我们定义了总共对五种请求方式的处理方法
          分别支持 GET(获取) POST(生成) PUT(更新) PATCH(局部更新) DELETE(删除)
          希望开发者分别利用好每种请求方式的不同来区分api功能
        2.  其中也有一些对tornado原有方法的重写以满足我们项目的需求
        3.  开发者可以进行适当修改和增添
    """
    __url__ = None

    # GET
    @tornado.gen.coroutine
    def get(self):
        pass

    # POST
    @tornado.gen.coroutine
    def post(self):
        pass

    # PUT
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        pass

    # PATCH
    @tornado.gen.coroutine
    def patch(self, *args, **kwargs):
        pass

    # DELETE
    @tornado.gen.coroutine
    def delete(self, *args, **kwargs):
        pass

    # 获取web后台登陆过来的安全cookie
    def get_current_user(self):
        if isinstance(self.get_secure_cookie("user"), bytes):
            return self.get_secure_cookie("user").decode('utf-8')
        else:
            return None

    @property
    def celery(self):
        return self.application.celery

    def data_received(self, chunk):
        pass

    # streng original torando get_argument method
    def streng_get_argument(self, value, default=None, match=None):
        # GET DELETE
        if self.request.method == 'GET' or self.request.method == 'DELETE':
            if match is not None:
                p1 = re.compile(match)
                match_res = p1.match(self.get_argument(value, default=''))
                if match_res:
                    return match_res.string
                else:
                    return None
            else:
                return self.get_argument(value, default=default)
        # POST PUT PATCH
        else:
            if self.get_argument(value, default=default) is None:
                if self.request.body:
                    try:
                        args = json.loads(self.request.body.decode('utf-8'))
                    except Exception:
                        args = {}
                    if value in args:
                        if match is not None:
                            p1 = re.compile(match)
                            match_res = p1.match(args[value] and args[value] or '')
                            if match_res:
                                return match_res.string
                            else:
                                return None
                        else:
                            return args[value]
                    else:
                        return None
                else:
                    return None
            else:
                if match is not None:
                    p1 = re.compile(match)
                    match_res = p1.match(self.get_argument(value, default=''))
                    if match_res:
                        return match_res.string
                    else:
                        return None
                else:
                    return self.get_argument(value, default=default)

    def check_token_security(self, is_jsonp=False, callback=None):
        if self.streng_get_argument("access_token", default=None):
            if verify_token(self.streng_get_argument("access_token")):
                return True
            else:
                if is_jsonp:
                    self.write_jsonp(callback, {'code': 401, 'msg': 'access_token is invalid!'})
                else:
                    self.write({'code': 401, 'msg': 'access_token is invalid!'})
        else:
            if is_jsonp:
                self.write_jsonp(callback, {'code': 401, 'msg': 'access_token is invalid!'})
            else:
                self.write({'code': 402, 'msg': 'missing access_token!'})
        return False

    def write_jsonp(self, callback, result):
        self.set_header('Content-Type', 'application/javascript')
        self.write("%s(%s)" % (callback, result))

    @staticmethod
    def dict2json(dictob):
        jsonstr = json.dumps(dictob, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8')
        return jsonstr
