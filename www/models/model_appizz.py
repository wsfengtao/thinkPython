#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from .db import *


# 生成唯一id
def next_id():
    return str(int(time.time() * 100))


# 用户基本信息集合
class User(Model):
    __database__ = 'test'
    __collection__ = 'users'

    _id = StringField(default=next_id)  # 用户报名号
    username = StringField()  # 用户姓名
    sex = IntegerField()  # 用户性别
    identy_card_number = StringField()  # 用户身份证号码
    driving_school = StringField(default='广科驾校')  # 用户报名驾校
    create_time = DoubleField(default=time.time())  # 用户注册时间


# 用户普通登陆方式账户信息集合
class AuthUser(Model):
    __database__ = 'test'
    __collection__ = 'auth_users'

    _id = StringField()  # 用户报名号
    tel_number = StringField()  # 用户手机号码
    email = StringField()  # 用户邮箱
    password = StringField()  # 用户密码


# 驾考题目
class DrivingTestSubject(Model):
    __database__ = 'test'
    __collection__ = 'drive_test_subject'

    city = StringField()  # 城市
    cycle_type = StringField()  # 车型
    kemu_type = IntegerField()  # 科目类型
    zhangjie = IntegerField()  # 章节
    tihao = IntegerField()  # 题号
    title = StringField()  # 题目内容
    is_single_selection = IntegerField()  # 题型
    answers = DictField()  # 答案
    right_answer = StringField()  # 正确答案
    img_src = StringField()  # 图片地址
    mp4_src = StringField()  # 视频地址
    reason = StringField()  # 答案分析
