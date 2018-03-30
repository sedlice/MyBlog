#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import hashlib

__author__ = "pyx"


def genearteMD5(pwd):
    "MD5加密方法"
    hl = hashlib.md5()
    hl.update(pwd.encode(encoding="utf-8"))
    return hl.hexdigest()