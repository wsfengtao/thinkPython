#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop
import logging
import tcelery
import os
import tornado.gen
import json
import socket
from tornado.tcpserver import TCPServer
from celery import Celery
from .config import app_config

__author__ = 'Geek_Feng'
__program__ = 'think_python'
__version__ = '0.0.1'

logging.basicConfig(level=logging.INFO)


class TcpConnection(object):
    """
    thinkPython服务端tcp连接处理类
    """

    def __init__(self, stream, address, clients, celery):
        self.stream = stream
        self._address = address
        self.stream.set_close_callback(self.on_close)
        self._clients = clients
        self._celery = celery
        self.EOF = b'\n'

    def __del__(self):
        self.streng_close()

    @tornado.gen.coroutine
    def start_tcp_session(self):
        rsp = yield self.read_message_until_b()
        if rsp is not False:
            r = yield tornado.gen.Task(self._celery.send_task, 'www.celery_tasks.task_rest_oauth.start_tcp_session',
                                       args=[rsp],
                                       queue='queue1')
            if r.state == 'SUCCESS':
                # 如果任务结果成功
                if r.result['code'] == 200:
                    # 如果有人已经登录
                    if r.result['tel_number'] in self._clients:
                        # 发送强制下线信息
                        yield self._clients[r.result['tel_number']].send_message(
                            {'code': 800, 'msg': 'you have been log off!'})
                        self._clients[r.result['tel_number']].streng_close()
                        yield self.send_message({'code': 200, 'msg': 'you log success!'})
                        # 将当前连接置入clients集合
                        self._clients[r.result['tel_number']] = self
                    # 如果没有人登录
                    else:
                        # 发送登录成功信息
                        yield self.send_message({'code': 200, 'msg': 'you log success!'})
                        # 将当前连接置入clients集合
                        self._clients[r.result['tel_number']] = self
                # 收到注销广播
                # todo:: 强制下线广播与注销广播特殊,对客户端是否接收不必须,其它广播需注意,发送失败必须备份
                elif r.result['code'] == "101":
                    if r.result['tel_number'] in self._clients:
                        # 发送注销信息
                        yield self._clients[r.result['tel_number']].send_message(
                            {'code': 801, 'msg': 'log off success!'})
                        self._clients[r.result['tel_number']].streng_close()
                        if r.result['tel_number'] in self._clients:
                            self._clients.pop(r.result['tel_number'])
                            self.streng_close()
                # 收到强制下线广播
                # todo:: 强制下线广播与注销广播特殊,对客户端是否接收不必须,其它广播需注意,发送失败必须备份
                elif r.result['code'] == "102":
                    if r.result['tel_number'] in self._clients:
                        # 发送强退信息
                        yield self._clients[r.result['tel_number']].send_message(
                            {'code': 800, 'msg': 'you have been log off!'})
                        self._clients[r.result['tel_number']].streng_close()
                        if r.result['tel_number'] in self._clients:
                            self._clients.pop(r.result['tel_number'])
                            self.streng_close()
                # 如果任务结果失败
                else:
                    yield self.send_message(r.result)
                    self.streng_close()
            else:
                yield self.send_message({'code': 888, 'msg': 'the server has problems!'})
                self.streng_close()

    @tornado.gen.coroutine
    def read_message_until_b(self):
        try:
            return (yield self.stream.read_until(b'\n'))
        except Exception as e:
            logging.error(str(e))
            return False

    @tornado.gen.coroutine
    def send_message(self, data):
        try:
            yield self.stream.write(json.dumps(data).encode('utf-8') + self.EOF)
        except Exception as e:
            logging.error(str(e))

    def streng_close(self):
        try:
            if not self.stream.closed():
                self.stream.close()
        except Exception as e:
            logging.error(str(e))

    def on_close(self):
        logging.info("the client %s has left", self._address)


class MonitorServer(TCPServer):
    """
    thinkPython服务端tcp服务器
    """

    def __init__(self):
        # init celery
        super().__init__()
        logging.info('init celery and set it in this app')
        my_celery = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
        my_celery.conf.CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'amqp')
        tcelery.setup_nonblocking_producer()
        self.celery = my_celery
        self._clients = dict()

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        # todo:: 此处未经测试,不知道是否能保持超越24小时长连接
        stream.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        logging.info("new connection %s %s", address, stream)
        conn = TcpConnection(stream, address, self._clients, self.celery)
        yield conn.start_tcp_session()


class Application(tornado.web.Application):
    """
    thinkPython服务端http服务器
    """

    def __init__(self):
        # set app url handle
        handlers = []
        adds_all_handles = os.path.join(os.path.dirname(__file__), "handles")
        lst_dir = os.walk(adds_all_handles)
        for handle_dir in lst_dir:
            lst = os.listdir(handle_dir[0])
            spt_dir = handle_dir[0].split('/')
            # Remove the root directory
            if spt_dir[-1] != 'handles':
                i = -1
                ab_dir = []
                while 1:
                    i -= 1
                    if spt_dir[i] == 'handles':
                        break
                    else:
                        continue
                while i is not 0:
                    ab_dir.append(str(spt_dir[i]))
                    if i is not -1:
                        ab_dir.append('.')
                    i += 1
                ab_dir = ''.join(ab_dir)
                ab_dir = 'www.' + ab_dir
                for adds_handle in lst:
                    if adds_handle.find('Handler.py') is not -1:
                        module_name = adds_handle.split('.py')[0]
                        _temp = __import__(ab_dir, globals(), locals(), [module_name])
                        now_module = getattr(_temp, str(module_name))
                        module_class = getattr(now_module, str(module_name))
                        handlers.append((module_class.__url__, module_class))
                        logging.info('add handle: %s in url : %s' % (module_class, module_class.__url__))

        # set other app settings
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            **app_config.app.settings
        )

        # init app
        logging.info('init app ...')
        super(Application, self).__init__(handlers, **settings)

        # init celery
        logging.info('init celery and set it in this app')
        my_celery = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
        my_celery.conf.CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'amqp')
        tcelery.setup_nonblocking_producer()
        self.celery = my_celery


def start_app():
    """
    启动http server服务(Application)
    Start HTTP Server(Application)
    """
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    logging.info('web server start at 127.0.0.1:%s ...', app_config.app.port)
    http_server.listen(app_config.app.port)
    tornado.ioloop.IOLoop.current().start()


def start_tcp_server():
    """
    启动tcp server服务(Application)
    Start TCP Server(Application)
    """
    tornado.options.parse_command_line()
    tcp_server = MonitorServer()
    logging.info('tcp server start at %s:%s ...', app_config.tcp.address, app_config.tcp.port)
    tcp_server.listen(port=app_config.tcp.port, address=app_config.tcp.address)
    tornado.ioloop.IOLoop.current().start()
