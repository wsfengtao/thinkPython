#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import json
from . import celery_server
from ..vender import *
from . import redis_pool

__author__ = 'Geek_Feng'

"""celery分布式任务组(REST 消息服务)"""


@celery_server.task
def send_email(to_sen, kemu):
    """发送邮件
    :param kemu: 科目数
    :param to_sen: 接收方
    :return: 返回dict状态组
    :rtype: dict
    """
    res = sendqqmail(to_sen, kemu)
    if isinstance(res, str):
        return {'code': 403, 'msg': res}
    else:
        return {'code': 200, 'msg': 'send success!'}


@celery_server.task
def vertify_pic_vertify_code(picvetifycode, pic_random_value):
    """验证图片验证码
    :param pic_random_value: 图片验证码编号
    :param picvetifycode: 图片验证码值
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    try:
        vertifypic = redis_cursor.get(pic_random_value)
        if vertifypic:
            if picvetifycode == vertifypic.decode('utf-8'):
                # 验证成功则销毁原图片验证码
                redis_cursor.delete(pic_random_value)
                return {'code': 200, 'msg': 'check picvetifycode success!'}
            else:
                return {'code': 414, 'msg': 'check picvetifycode error!'}
        else:
            return {'code': 415, 'msg': 'No picvetifycode exit!'}
    except Exception as e:
        return {'code': 416, 'msg': str(e)}


@celery_server.task
def generate_pic_vertify_code():
    """生成图片验证码
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    try:
        all_bchar, b64img = rndpic()
        # 生成随机value
        pic_random_value = get_pic_random_value()
        redis_cursor.set(pic_random_value, all_bchar)
        # 有效时间5分钟
        redis_cursor.expire(pic_random_value, 300)
        return {'code': 200, 'msg': "get picverty code success!", 'b64img': b64img.decode("utf-8"),
                'pic_random_value': pic_random_value}
    except Exception as e:
        return {'code': 416, 'msg': str(e)}


@celery_server.task
def generate_and_send_sms_vertify_code(picvetifycode, pic_random_value, tel_number):
    """生成并发送短信验证码
    :param pic_random_value: 图片验证码编号
    :param picvetifycode: 图片验证码值
    :param tel_number: 用户手机号码
    :return: 返回dict状态组
    :rtype: dict
    """
    redis_cursor = redis.Redis(connection_pool=redis_pool)
    try:
        vertifypic = redis_cursor.get(pic_random_value)
        if vertifypic:
            if picvetifycode == vertifypic.decode('utf-8'):
                # 验证成功则销毁原图片验证码
                redis_cursor.delete(pic_random_value)
                # 调用阿里大鱼api发送短信
                req = Alibabasms(key='23347085', secret='1151632fea3afdb7934810236f6fbf51')
                req.sms_type = "normal"
                req.sms_free_sign_name = "登录验证"
                vertify_code = generate_verification_code()
                # 将短信验证码存入缓存
                redis_cursor.hset('sms_vertify_code', tel_number, vertify_code)
                req.sms_param = json.dumps({'code': vertify_code, 'product': '广科驾校'})
                req.rec_num = tel_number
                req.sms_template_code = "SMS_7770405"
                try:
                    r = req.get_response()
                    if 'error_response' in r:
                        return {'code': 413,
                                'msg': 'send sms failed! for the reason: ' + r['error_response']['sub_code']}
                    return {'code': 200, 'msg': 'send sms success!'}
                except Exception as e:
                    return {'code': 413, 'msg': 'send sms failed! for the reason: ' + str(e)}
            else:
                return {'code': 414, 'msg': 'check picvetifycode error!'}
        else:
            return {'code': 415, 'msg': 'No picvetifycode has been work out!'}
    except Exception as e:
        return {'code': 500, 'msg': str(e)}
