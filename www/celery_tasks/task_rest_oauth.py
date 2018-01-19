#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import json
import json.decoder
from . import celery_server
from ..vender import *
from . import redis_pool

__author__ = 'Geek_Feng'

"""celery分布式任务组(REST 认证服务)"""


@celery_server.task
def generate_oauth_code(app_secret):
    """根据传入的app平台密钥生成access_token
    :param app_secret: app平台唯一密钥
    :return: 返回dict状态组
    :rtype: dict
    """
    if app_secret == 'GxustCarb23cz9j2k1lqpknbjd':
        token = gen_token(app_secret)
        return {'code': 200, 'msg': 'success', 'access_token': token, 'expires_in': 7200}
    else:
        return {'code': 409, 'msg': "Your app_secret is wrong!"}


@celery_server.task
def start_tcp_session(rsp):
    """根据传入的数据决定是否保持tcp连接
    :param rsp: tcpclient 传来的bytes 需要转成Json
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    try:
        rsp_dict = json.loads(rsp.decode('utf-8'))
        if 'app_session_id' and 'tel_number' in rsp_dict:
            # 广播请求
            if rsp_dict['app_session_id'] == 'ngiekxojfnelskdkienglosk12mcls':
                return {'code': rsp_dict['command'], 'tel_number': rsp_dict['tel_number']}
            # 正常连接
            else:
                res = redis_cursor.hget('session', rsp_dict['tel_number'])
                if res:
                    if isinstance(res, bytes):
                        if rsp_dict['app_session_id'] == res.decode('utf-8'):
                            return {'code': 200, 'msg': 'app_session_id is right!',
                                    'tel_number': rsp_dict['tel_number']}
                        else:
                            return {'code': 444, 'msg': 'app_session_id is wrong!'}
                else:
                    return {'code': 446, 'msg': 'app_session_id is not exist!'}
        else:
            return {'code': 445, 'msg': 'not found app_session_id!'}
    except json.decoder.JSONDecodeError:
        return {'code': 444, 'msg': 'app_session_id is wrong!'}
