#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
from . import celery_server
from . import send_broadcast
from ..vender import *
from ..models import *
from . import db
from . import redis_pool

__author__ = 'Geek_Feng'

"""celery分布式任务组(REST 用户服务)"""


@celery_server.task
def user_login(login_type, tel_number, email, password):
    """用户登录
    :param login_type: 登录类型
    :param tel_number: 手机号码
    :param email: 邮箱号
    :param password: 用户密码
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    res = None
    if login_type == '1':
        res = AuthUser.find_one(db=db, filter={'tel_number': tel_number})
    elif login_type == '2':
        res = AuthUser.find_one(db=db, filter={'email': email})
    if res:
        if password == res['password']:
            app_session_id = get_app_session_id(res['tel_number'])
            redis_cursor.hset('session', res['tel_number'], app_session_id)
            # 发送强制下线广播
            send_broadcast(command="102", tel_number=res['tel_number'])
            return {'code': 200,
                    'msg': "Login success!",
                    'tel_number': res['tel_number'],
                    'email': res['email'],
                    'password': password,
                    'app_session_id': app_session_id
                    }
        else:
            return {'code': 603, 'msg': "password is not correct!"}
    else:
        return {'code': 408, 'msg': "Can't find this user!"}


@celery_server.task
def user_logout(tel_number, password):
    """用户注销
    :param tel_number: 手机号码
    :param password: 用户密码
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    res = AuthUser.find_one(db=db, filter={'tel_number': tel_number, 'password': password})
    if res:
        # 原子性注销
        res2 = redis_cursor.hdel('session', tel_number)
        if res2:
            # 发送注销广播
            send_broadcast(command="101", tel_number=tel_number)
            return {'code': 200, 'msg': "Log out success!"}
        else:
            return {'code': 506, 'msg': "this user Already have been logout!"}
    else:
        return {'code': 508, 'msg': "Can't find this user!"}


@celery_server.task
def update_user_information(smsvetifycode, tel_number, password, new_password):
    """更新用户密码
    :param smsvetifycode: 短信验证码
    :param tel_number: 手机号码
    :param password: 用户老密码
    :param new_password: 用户新密码
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    # 验证(每个验证码只能进行一次验证,不能进行重复验证,验证成功即返回空{},否则含有'error'和'code'键)
    res5 = redis_cursor.hget('sms_vertify_code', tel_number)
    if res5:
        # 验证失败
        if res5.decode('utf-8') != smsvetifycode:
            return {'code': 417, 'msg': "check smsvetifycode error!"}
        # 验证成功
        else:
            redis_cursor.hdel('sms_vertify_code', tel_number)
            # 原子性更改密码
            res = AuthUser.find_one_and_update(db=db, filter={'password': password, 'tel_number': tel_number},
                                               update={'$set': {'password': new_password}})
            if res:
                return {'code': 200, 'msg': "Update password success!"}
            else:
                return {'code': 412, 'msg': "Update password failed!"}
    else:
        return {'code': 417, 'msg': "check smsvetifycode error!"}


@celery_server.task
def register_new_user(smsvetifycode, tel_number, password, email, apply_id):
    """注册新的用户
    :param smsvetifycode: 短信验证码
    :param tel_number: 手机号码
    :param password: 密码
    :param email: 用户邮箱
    :param apply_id: 用户报名码
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    res = User.find_one(db=db, filter={'_id': apply_id})
    if res:
        res4 = AuthUser.find_one(db=db, filter={'$or': [{'tel_number': tel_number}, {'email': email}]})
        if res4:
            return {'code': 420, 'msg': "Already have this user!"}
        else:
            # 验证(每个验证码只能进行一次验证,不能进行重复验证,验证成功即返回空{},否则含有'error'和'code'键)
            res5 = redis_cursor.hget('sms_vertify_code', tel_number)
            # 验证失败
            if res5.decode('utf-8') != smsvetifycode:
                return {'code': 417, 'msg': "check smsvetifycode error!"}
            # 验证成功
            else:
                redis_cursor.hdel('sms_vertify_code', tel_number)
                user = AuthUser(_id=res['_id'], tel_number=tel_number, password=password, email=email)
                res3 = user.insert_one(db=db)
                if res3:
                    return {'code': 200,
                            'msg': "register success!",
                            'apply_id': apply_id,
                            'tel_number': tel_number,
                            'email': email,
                            'password': password,
                            'name': res['username'],
                            'sex': res['sex'],
                            'identy_card_number': res['identy_card_number'],
                            'driving_school': res['driving_school'],
                            'create_time': res['create_time']}
                else:
                    return {'code': 411, 'msg': "databases error!"}
    else:
        return {'code': 410, 'msg': "Can't find this applyid!"}


@celery_server.task
def get_user_information(tel_number, password):
    """根据传入的用户账户密码获取用户具体信息
    :param tel_number: 要查询的用户手机号码
    :param password: 要查询的用户密码
    :return: 返回dict状态组
    :rtype: dict
    """
    res = AuthUser.find_one(db=db, filter={'tel_number': tel_number})
    if res:
        res2 = User.find_one(db=db, filter={'_id': res['_id']})
        if res2:
            if res['password'] == password:
                return {'code': 200,
                        'msg': "get user success!",
                        'apply_id': res['_id'],
                        'tel_number': tel_number,
                        'email': res['email'],
                        'password': res['password'],
                        'name': res2['username'],
                        'sex': res2['sex'],
                        'identy_card_number': res2['identy_card_number'],
                        'driving_school': res2['driving_school'],
                        'create_time': res2['create_time']}
            else:
                return {'code': 488, 'msg': "password is not correct!"}
        else:
            return {'code': 412, 'msg': "Can't find register!"}
    else:
        return {'code': 412, 'msg': "Can't find register!"}
