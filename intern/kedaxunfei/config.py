#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Soraichi Kaku
# @Date  : 2024/7/20
# @Desc  :

import os

class Config():
    def __init__(self, appid: str = None, apikey: str = None, apisecret: str = None):
        '''
        讯飞API统一的环境配置
        :param appid: appid
        :param apikey: api key
        :param apisecret: api secret

        调用方式：
        # 加载系统环境变量SPARKAI_APP_ID、SPARKAI_API_KEY、SPARKAI_API_SECRET
        # 系统环境变量需要进行赋值
        config = Config()
        # 自定义key写入
        config = Config('14****93', 'eb28b****b82', 'MWM1MzBkOD****Mzk0')
        '''
        if appid is None:
            self.XF_APPID = os.environ["SPARKAI_APP_ID"]
        else:
            self.XF_APPID = appid
        if apikey is None:
            self.XF_APIKEY = os.environ["SPARKAI_API_KEY"]
        else:
            self.XF_APIKEY = apikey
        if apisecret is None:
            self.XF_APISECRET = os.environ["SPARKAI_API_SECRET"]
        else:
            self.XF_APISECRET = apisecret
