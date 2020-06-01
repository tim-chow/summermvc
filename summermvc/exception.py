# coding: utf8

__authors__ = ["Tim Chow"]


# 所有异常类的基类
class IOCError(StandardError):
    pass


# AOP 异常的基类
class AOPError(IOCError):
    pass


class DuplicatedBeanNameError(IOCError):
    pass


class BeanNotFoundError(IOCError):
    pass


class UnavailableBeanClassError(IOCError):
    pass


# 用来从通知中返回值
class Return(Exception):
    def __init__(self, return_value, *a):
        Exception.__init__(self, *a)
        self._return_value = return_value

    def get_return_value(self):
        return self._return_value
