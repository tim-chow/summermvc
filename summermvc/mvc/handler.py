# coding: utf8

"""
Handler 对象包含 page handler 和若干个 exception handler
"""

from ..utility import is_tornado_installed


class Handler(object):
    def __init__(self):
        self._page_handler = None
        self._matches = None
        self._exception_handlers = {}

    def __nonzero__(self):
        return self.page_handler is not None

    def invoke(self, *a, **kw):
        if self.page_handler is None:
            raise RuntimeError("no page handler specified")
        return self.page_handler(*a, **kw)

    def add_page_handler(self, page_handler, matches=None):
        self._page_handler = page_handler
        self._matches = matches

    def add_exception_handler(self, exception, exception_handler, matches=None):
        self._exception_handlers[exception] = exception_handler, matches

    @property
    def page_handler(self):
        return self._page_handler

    @property
    def matches(self):
        return self._matches

    @property
    def exception_handlers(self):
        return self._exception_handlers


if is_tornado_installed:
    import tornado.gen as gen


    class TornadoHandler(Handler):
        @gen.coroutine
        def invoke(self, *a, **kw):
            if self.page_handler is None:
                raise RuntimeError("no page handler specified")
            return_value = self.page_handler(*a, **kw)
            if gen.is_future(return_value):
                result = yield return_value
                raise gen.Return(result)
            raise gen.Return(return_value)

