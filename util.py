#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import re
import os


def upload(file):
    "上传方法"
    if file is not None:
        filesuffix = (file.filename.split("."))[-1]
        filename = str(datetime.datetime.now())
        reg = re.compile("\\W")
        filename = reg.sub("", filename)
        filename = filename + "." + filesuffix
        file.save(os.path.join("static/images", filename))
        return filename
    else:
        return ""
