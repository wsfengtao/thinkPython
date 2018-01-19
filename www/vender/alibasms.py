#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib import parse
import hashlib
import requests
from time import time

__author__ = 'Geek_Feng'


class Alibabasms(object):
    """阿里大鱼短信发送api(Python3版本 版本>=3.4)(坑比阿里官方竟然没有Python3的版本 233333)"""

    def __init__(self, key, secret, url="http://gw.api.taobao.com/router/rest", partner_id=""):
        self.key = key
        self.secret = secret
        self.url = url
        self.partner_id = partner_id

    def sign(self, params):
        # ===========================================================================
        # '''签名方法
        # @param parameters: 支持字典和string两种
        # '''
        # ===========================================================================
        if isinstance(params, dict):
            params = "".join(["".join([k, v]) for k, v in sorted(params.items())])
            params = "".join([self.secret, params, self.secret])
        sign = hashlib.md5(params.encode("utf-8")).hexdigest().upper()
        return sign

    def get_api_params(self):
        params = {}
        try:
            [params.__setitem__(k, getattr(self, k)) for k in Alibabasms.get_param_names()]
        except AttributeError:
            raise Exception("Some parameters is needed for this api call")
        [params.__setitem__(k, getattr(self, k)) for k in Alibabasms.get_option_names() if hasattr(self, k)]
        return params

    @staticmethod
    def get_api_name():
        return "alibaba.aliqin.fc.sms.num.send"

    @staticmethod
    def get_param_names():
        return ['sms_type', 'sms_free_sign_name', 'rec_num', 'sms_template_code']

    @staticmethod
    def get_option_names():
        return ['extend', 'sms_param']

    def get_response(self, authorize=None):
        """调用阿里大鱼api发送大鱼短信

        :param str authorize: session授权码(短信api不需要授权码)
        :return: 如果采用yield获得的返回值为阿里大鱼返回码,直接调用返回值为生成器
        :rtype: str or generator
        """
        sys_params = {
            "method": Alibabasms.get_api_name(),
            "app_key": self.key,
            "timestamp": str(int(time() * 1000)),
            "format": "json",
            "v": "2.0",
            "partner_id": self.partner_id,
            "sign_method": "md5",
        }
        if authorize is not None:
            sys_params['session'] = authorize
        params = self.get_api_params()
        sign_params = sys_params.copy()
        sign_params.update(params)
        sys_params['sign'] = self.sign(sign_params)
        headers = {
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive"
        }
        sys_params.update(params)
        sys_params = parse.urlencode(sys_params)
        r = requests.post(self.url, params=sys_params, headers=headers)
        r.raise_for_status()
        return r.json()
