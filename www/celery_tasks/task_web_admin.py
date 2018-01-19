#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import time
from . import celery_server
from ..models import *
from . import db

__author__ = 'Geek_Feng'

"""celery分布式任务组(WEB 后台服务)"""


@celery_server.task
def delete_student(deletestus):
    """删除学员基本信息
    :param deletestus: 学员信息列表
    :return: 返回dict状态组
    :rtype: dict
    """
    filter = {'$or': []}
    if isinstance(deletestus, list):
        filter['$or'] = [{'_id': value} for value in deletestus]
    res = User.delete_all(db=db, filter=filter)
    res2 = AuthUser.delete_all(db=db, filter=filter)
    if res and res2:
        return {'code': 200, 'msg': 'delete ok!'}


@celery_server.task
def add_new_student(apply_id, username, identy_card_number, sexpicked):
    """新增学员信息
    :param apply_id: 学员报名号
    :param username: 学员姓名
    :param identy_card_number: 学员身份证信息
    :param sexpicked: 学员性别
    :return: 返回dict状态组
    :rtype: dict
    """
    res = User.find_one(db=db, filter={
        '$or': [{'_id': apply_id}, {'username': username}, {'identy_card_number': identy_card_number}]})
    if res:
        return {'code': 404, 'msg': 'Already have this user!'}
    else:
        sexpicked = (1 if sexpicked == 'option1' else 0)
        user = User(_id=apply_id, username=username, sex=sexpicked, identy_card_number=identy_card_number,
                    create_time=time.time())
        res2 = user.insert_one(db=db)
        if res2:
            return {'code': 200, 'msg': "insert success!"}
        else:
            return {'code': 411, 'msg': "databases error!"}


@celery_server.task
def get_page_student(nowpage):
    """获取当前页学生信息
    :param nowpage: 页数
    :return: 返回dict状态组
    :rtype: dict
    """
    res = User.find_all(db=db)
    res = res.sort('create_time', -1).limit(8).skip((nowpage - 1) * 8)
    allpage = math.ceil(res.count() / 8) if math.ceil(res.count() / 8) else 1
    json_res = {}
    i = 1
    for x in res:
        json_res[i] = x
        i += 1
    json_res['nowpage'] = nowpage
    json_res['allpage'] = allpage
    return json_res
