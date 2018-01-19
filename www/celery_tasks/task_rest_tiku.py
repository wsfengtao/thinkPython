#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import celery_server
from ..models import *
from . import db

__author__ = 'Geek_Feng'

"""celery分布式任务组(REST 题库服务)"""


@celery_server.task
def get_qs_list(city, cycle_type, kemu_type, zhangjie, start_tihao, size):
    """根据传入的参数获取一组驾考题的全部信息
    :param city: 城市
    :param cycle_type: 车型
    :param kemu_type: 科目类型
    :param zhangjie: 科目章节
    :param start_tihao: 开始题号
    :param size: 范围长度
    :return: 返回dict状态组
    :rtype: dict
    """
    res = DrivingTestSubject.find_all(db=db,
                                      filter={'city': city, 'cycle_type': cycle_type, 'kemu_type': int(kemu_type),
                                              'zhangjie': int(zhangjie),
                                              'tihao': {'$lte': (int(start_tihao) + int(size) - 1),
                                                        '$gte': int(start_tihao)}})
    if res:
        qs_list = [x for x in res]
        for qs in qs_list:
            qs.pop('_id')
        return {'code': 200, 'msg': 'get success!', 'qs_list': qs_list}
    else:
        return {'code': 917, 'msg': 'get qs list failed!'}


@celery_server.task
def get_qs_size(city, cycle_type, kemu_type, zhangjie):
    """根据传入的参数获取一组驾考题的size
    :param city: 城市
    :param cycle_type: 车型
    :param kemu_type: 科目类型
    :param zhangjie: 科目章节
    :return: 返回dict状态组
    :rtype: dict
    """
    res = DrivingTestSubject.count(db=db, filter={'city': city, 'cycle_type': cycle_type, 'kemu_type': int(kemu_type),
                                                  'zhangjie': int(zhangjie)})
    if res:
        return {'code': 200, 'msg': 'get success!', 'qs_size': res}
    else:
        print(res)
        return {'code': 917, 'msg': 'get qs size failed!'}
