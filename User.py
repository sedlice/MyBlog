#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class User(object):
    def __init__(self):
        self.uid = 0
        self.username = ""
        self.imgpath = ""
        self.realname = ""
        self.access = 0
        self.description = ""

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def realname(self):
        return self._realname

    @realname.setter
    def realname(self, value):
        self._realname = value

    @property
    def imgpath(self):
        return self._imgpath

    @imgpath.setter
    def imgpath(self, value):
        self._imgpath = value

    @property
    def access(self):
        return self._access

    @access.setter
    def access(self, value):
        self._access = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
