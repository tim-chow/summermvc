# coding: utf8

__all__ = ["AutoWiredField", "ValueField"]
__authors__ = ["Tim Chow"]


class AutoWiredField(object):
    def __init__(self, auto_wired=None):
        self._auto_wired = auto_wired

    @property
    def auto_wired(self):
        return self._auto_wired


class ValueField(object):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value
