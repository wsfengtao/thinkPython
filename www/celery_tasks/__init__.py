#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import redis
import os
import socket
from celery import Celery, platforms
from ..config import app_config

__author__ = 'Geek_Feng'

# Redis 客户端
redis_pool = redis.ConnectionPool(max_connections=500, host='localhost', port=6379, db=0)

# Mongodb 客户端
db = pymongo.MongoClient(**app_config.db.db_settings)

platforms.C_FORCE_ROOT = True
celery_server = Celery('tasks', broker='amqp://guest:guest@localhost:5672//',
                       include=['www.celery_tasks.task_rest_message', 'www.celery_tasks.task_rest_oauth',
                                'www.celery_tasks.task_rest_users', 'www.celery_tasks.task_web_admin',
                                'www.celery_tasks.task_rest_tiku'])
celery_server.conf.CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'amqp')


def send_broadcast(command, **kwargs):
    # todo:: socket没有复用,每次都要在线程中重开socket,以后有可能做一个根据线程id复用socket的socket_pool
    """发送广播
    :param command: 广播命令
    :param kwargs: 其他参数
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_is_ok = True
    try:
        # 建立连接:
        s.connect(('127.0.0.1', app_config.tcp.port))
        try:
            # 发送注销广播:
            if command == "101":
                if kwargs['tel_number']:
                    s.send(
                        b'{"app_session_id":"ngiekxojfnelskdkienglosk12mcls", "command": "' + command.encode(
                            'utf-8') + b'"' + b', "tel_number":"' +
                        kwargs['tel_number'].encode('utf-8') + b'"}\n')
        except Exception:
            pass
    except Exception:
        connect_is_ok = False
    finally:
        if connect_is_ok:
            s.close()

# def dict2json(dictob):
#     """将传入的dict转换成bytes
#     :param dictob: dict字典
#     :return: 返回转换完成的bytes
#     :rtype: bytes
#     """
#     jsonstr = json.dumps(dictob, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8')
#     return jsonstr
