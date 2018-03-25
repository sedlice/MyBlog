#!/usr/bin/env python
# -*- coding: utf-8 -*-


import psutil

pc_mem = psutil.virtual_memory()

div_gb_factor = (1024.0 ** 3)
print("total memory: %f GB" % float(pc_mem.total / div_gb_factor))
print("available memory: %f GB" % float(pc_mem.available / div_gb_factor))
print("used memory: %f GB" % float(pc_mem.used / div_gb_factor))
print("percent of used memory: %f" % float(pc_mem.percent))
print("free memory: %f GB" % float(pc_mem.free / div_gb_factor))
