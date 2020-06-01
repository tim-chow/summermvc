# coding: utf8

__all__ = ["HandlerExecutionChain"]
__authors__ = ["Tim Chow"]

from .exception import InterceptError
from ..utility import is_tornado_installed


class HandlerExecutionChain(object):
    def __init__(self, handler, interceptors):
        self._handler = handler
        self._interceptors = interceptors

    def handle(self, request, response, mv, *args, **kwargs):
        # 执行拦截器的 pre handle 链
        for interceptor in self.interceptors:
            try:
                interceptor.pre_handle(request, response, mv)
            except InterceptError:
                return

        # 执行 handler
        result = self.handler.invoke(*args, **kwargs)

        # 执行拦截器的 post handle 链
        for interceptor in self.interceptors:
            try:
                interceptor.post_handle(request, response, mv)
            except InterceptError:
                break

        return result

    @property
    def handler(self):
        return self._handler

    @property
    def interceptors(self):
        return self._interceptors


if is_tornado_installed:
    import tornado.gen as gen


    class TornadoHandlerExecutionChain(HandlerExecutionChain): 
        @gen.coroutine
        def handle(self, request, response, mv, *args, **kwargs):
            # 执行拦截器的 pre handle 链
            for interceptor in self.interceptors:
                try:
                    return_value = interceptor.pre_handle(
                        request,
                        response,
                        mv)
                    if gen.is_future(return_value):
                        yield return_value
                except InterceptError:
                    raise gen.Return()

            # 执行 handler
            return_value = self.handler.invoke(*args, **kwargs)
            if gen.is_future(return_value):
                result = yield return_value
            else:
                result = return_value

            # 执行拦截器的 post handle 链
            for interceptor in self.interceptors:
                try:
                    return_value = interceptor.post_handle(
                        request,
                        response,
                        mv)
                    if gen.is_future(return_value):
                        yield return_value
                except InterceptError:
                    break

            raise gen.Return(result)

