#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"模块说明"

__author__ = "pyx"

import psutil

prom = [0, 0, 0]
pc = psutil.disk_partitions()
for i in pc:
    pc_disk = psutil.disk_usage(i[0])
    prom[0] = prom[0] + pc_disk[0]
    prom[1] = prom[1] + pc_disk[1]
    prom[2] = prom[2] + pc_disk[2]
a = "%.2f" % (prom[0] / (1024**3))
b = "%.2f" % (prom[1] / (1024**3))
c = "%.2f" % (prom[2] / (1024**3))
print(a, b, c)
