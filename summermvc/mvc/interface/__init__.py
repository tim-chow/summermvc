# coding: utf8

__all__ = [
    "Ordered",
    "HandlerMapping",
    "HandlerAdapter",
    "HandlerInterceptor",
    "ViewResolver",
    "View"]
__authors__ = ["Tim Chow"]

from abc import ABCMeta, abstractmethod


class Ordered(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_order(self):
        pass


class HandlerAdapter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def supports(self, handler):
        pass

    @abstractmethod
    def handle(self, request, response, handler_execution_chain):
        pass


class HandlerMapping(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_handler(self, request):
        pass


class HandlerInterceptor(Ordered):
    __metaclass__ = ABCMeta

    @abstractmethod
    def pre_handle(self, request, response, model_and_view):
        pass

    @abstractmethod
    def post_handle(self, request, response, model_and_view):
        pass

    @abstractmethod
    def path_pattern(self):
        pass


class ViewResolver(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_view(self, view_name, status_code):
        pass


class View(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self, model):
        pass

    @abstractmethod
    def get_content_type(self):
        pass
