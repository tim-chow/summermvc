# coding: utf8

__all__ = ["DispatcherConfigurer",
           "DefaultDispatcherConfigurer"]
__authors__ = ["Tim Chow"]

from abc import ABCMeta, abstractproperty


class DispatcherConfigurer(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def max_redirect_count(self):
        pass

    @abstractproperty
    def context_path(self):
        pass


class DefaultDispatcherConfigurer(DispatcherConfigurer):
    @property
    def max_redirect_count(self):
        return 100

    @property
    def context_path(self):
        return None

