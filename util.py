#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import hashlib

__author__ = "pyx"
# 根据ip查询城市接口 http://ip.taobao.com/service/getIpInfo.php?ip=110.84.0.129


def genearteMD5(pwd):
    "MD5加密方法"
    hl = hashlib.md5()
    hl.update(pwd.encode(encoding="utf-8"))
    return hl.hexdigest()