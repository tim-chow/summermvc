# coding: utf8

__all__ = ["RequestMappingHandlerMapping"]
__authors__ = ["Tim Chow"]

import re

from .interface import HandlerMapping
from ..decorator import *
from .handler import Handler
from ..reflect import get_declared_methods
from ..utility import is_tornado_installed


class RequestMappingHandlerMapping(HandlerMapping):
    @property
    def handler_class(self):
        return Handler

    def can_handle(self, cls):
        return is_rest_controller_present(cls)

    def get_handler(self, request):
        handler = self.handler_class()
        for bean_name, bean_obj in request.application_context.iter_beans():
            cls = bean_obj.cls
            if not self.can_handle(cls):
                continue
            obj = request.application_context.get_bean(bean_name)
            for attr_name, method in get_declared_methods(cls):
                class_mvc_args = get_request_mapping(cls)
                method_mvc_args = get_request_mapping(method)
                method_exception_handler = get_exception_handler(method)
                if method_mvc_args:
                    uri_pattern = (class_mvc_args and class_mvc_args["uri"] or "") + \
                            (method_mvc_args and method_mvc_args["uri"] or "")
                    uri_pattern = uri_pattern.endswith("$") and uri_pattern or (uri_pattern + "$")
                    m = re.match(uri_pattern, request.uri)
                    if m:
                        consumes = method_mvc_args["consumes"]
                        if not consumes or request.content_type in consumes:
                            matches = dict(zip(map(str, range(1, len(m.groups())+1)), m.groups()))
                            matches.update(m.groupdict() or {})
                            wanted_request_method = method_mvc_args["method"]
                            if wanted_request_method is None and not handler:
                                handler.add_page_handler(getattr(obj, attr_name), matches)
                            elif wanted_request_method and \
                                    wanted_request_method == request.request_method:
                                handler.add_page_handler(getattr(obj, attr_name), matches)
                if method_exception_handler:
                    uri_pattern = (class_mvc_args and class_mvc_args["uri"] or "") + \
                            (method_exception_handler and method_exception_handler["uri"] or "")
                    uri_pattern = uri_pattern.endswith("$") and uri_pattern or (uri_pattern + "$")
                    m = re.match(uri_pattern, request.uri)
                    if m:
                        matches = dict(zip(map(str, range(1, len(m.groups())+1)), m.groups()))
                        matches.update(m.groupdict() or {})
                        for exc in method_exception_handler["exceptions"]:
                            handler.add_exception_handler(
                                exc,
                                getattr(obj, attr_name),
                                matches)
        return handler or None


if is_tornado_installed:
    __all__.append("TornadoRequestMappingHandlerMapping")

    from ..decorator import is_tornado_rest_controller_present
    from .handler import TornadoHandler


    class TornadoRequestMappingHandlerMapping(
            RequestMappingHandlerMapping):
        @property
        def handler_class(self):
            return TornadoHandler

        def can_handle(self, cls):
            return is_tornado_rest_controller_present(cls)

