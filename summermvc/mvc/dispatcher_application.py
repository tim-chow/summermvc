# coding: utf8

__all__ = ["BaseDispatcher",
           "DispatcherApplication"]
__authors__ = ["Tim Chow"]

import re
import types
import logging
import traceback
import threading

from .http_utility import *
from .model_and_view import *
from .interface import *
from .exception import *
from .json_view_resolver import JsonViewResolver
from .request_mapping_handler_mapping import *
from .request_mapping_handler_adapter import *
from .handler_execution_chain import *
from .constant import HTTPStatus
from ..application_context import ApplicationContext
from .dispatcher_configurer import *
from ..utility import is_tornado_installed

LOGGER = logging.getLogger(__name__)


class _Factory(object):
    """享元工厂"""
    _lock = threading.Lock()
    _objs = {}

    def __new__(cls, ctx):
        assert isinstance(ctx, ApplicationContext), \
            "ApplicationContext expected"
        key = (id(cls), id(ctx))
        if key in _Factory._objs:
            return _Factory._objs[key]

        with _Factory._lock:
            if key in _Factory._objs:
                return _Factory._objs[key]

            obj = object.__new__(cls)
            obj.initialize(ctx)
            _Factory._objs[key] = obj
            return obj

    def initialize(self, *args, **kwargs):
        pass


class BaseDispatcher(_Factory):
    def initialize(self, application_context):
        self._ctx = application_context
        self._handler_mappings = []
        self._handler_interceptors = []
        self._handler_adapters = []
        self._view_resolver = JsonViewResolver()
        for name, bean in self._ctx.iter_beans():
            obj = self._ctx.get_bean(name)
            if issubclass(bean.cls, HandlerMapping):
                self._handler_mappings.append(obj)
            if issubclass(bean.cls, HandlerInterceptor):
                self._handler_interceptors.append(obj)
            if issubclass(bean.cls, HandlerAdapter):
                self._handler_adapters.append(obj)
            if issubclass(bean.cls, ViewResolver):
                self._view_resolver = obj

        self._configurer = DefaultDispatcherConfigurer()
        self._default_handler_mapping = RequestMappingHandlerMapping()
        self._chain_class = HandlerExecutionChain
        self._default_handler_adapter = RequestMappingHandlerAdapter()

    @property
    def application_context(self):
        return self._ctx

    @property
    def handler_mappings(self):
        return self._handler_mappings

    @property
    def handler_interceptors(self):
        return self._handler_interceptors

    @property
    def handler_adapters(self):
        return self._handler_adapters

    @property
    def view_resolver(self):
        return self._view_resolver

    @property
    def configurer(self):
        return self._configurer

    @configurer.setter
    def configurer(self, configurer):
        self._configurer = configurer

    @property
    def default_handler_mapping(self):
        return self._default_handler_mapping

    @default_handler_mapping.setter
    def default_handler_mapping(self, default_handler_mapping):
        self._default_handler_mapping = default_handler_mapping

    @property
    def chain_class(self):
        return self._chain_class

    @chain_class.setter
    def chain_class(self, chain_class):
        self._chain_class = chain_class

    @property
    def default_handler_adapter(self):
        return self._default_handler_adapter

    @default_handler_adapter.setter
    def default_handler_adapter(self, default_handler_adapter):
        self._default_handler_adapter = default_handler_adapter

    def get_handler(self, request):
        for handler_mapping in self.handler_mappings:
            handler = handler_mapping.get_handler(request)
            if handler is not None:
                return handler
        return self._default_handler_mapping.get_handler(request)

    def get_interceptors(self, uri):
        interceptors = []
        for interceptor in self.handler_interceptors:
            if re.match(interceptor.path_pattern(), uri):
                interceptors.append(interceptor)

        # 按照 order 对 interceptors 进行排序
        return sorted(interceptors, key=lambda i: i.get_order(), reverse=True)

    def get_execution_chain(self, request):
        handler = self.get_handler(request)
        if handler is None:
            raise NoHandlerFoundError("no handler found")
        interceptors = self.get_interceptors(request.uri)
        return self._chain_class(handler, interceptors)

    def get_adapter(self, handler):
        for handler_adapter in self.handler_adapters:
            if handler_adapter.supports(handler):
                return handler_adapter
        if self._default_handler_adapter.supports(handler):
            return self._default_handler_adapter
        return None

    def handle_request(self, chain, request, response):
        adapter = self.get_adapter(chain.handler)
        if adapter is None:
            raise NoAdapterFoundError("no adapter found")

        return adapter.handle(request, response, chain)

    def remove_context_path(self, request):
        # 去掉context path
        context_path = self.configurer.context_path
        if context_path is not None:
            if not request.uri.startswith(context_path):
                raise NoHandlerFoundError(
                    "uri must start with context path %s" % context_path)
            request.uri = request.uri[len(context_path):] or "/"

    def process_internal_redirect(self, request, response):
        if response.internal_redirect_to is not None:
            request.uri = response.internal_redirect_to
            response.clear()
            return True
        return False

    def process_exception(self, exception, response, mv):
        if isinstance(
                exception,
                (NoHandlerFoundError, NoAdapterFoundError)):
            response.set_status(HTTPStatus.NotFound)
            mv.model.add_attribute("info", "no handler or adapter found")
        else:
            LOGGER.error("fail to process request", exc_info=True)
            response.set_status(HTTPStatus.InternalError)
            mv.model.add_attribute("traceback", traceback.format_exc())

    def rend(self, mv, response):
        view_object = self.view_resolver.get_view(
            mv.view,
            response.status_code)
        body = view_object.render(mv.model)
        content_type = view_object.get_content_type()
        response.add_header("Content-Length", str(len(body)))
        if content_type is not None:
            response.add_header("Content-Type", content_type)
        return body


class DispatcherApplication(BaseDispatcher):
    def __call__(self, environment, start_response):
        request = Request.from_wsgi_environment(
            environment,
            self.application_context)
        response = Response()
        mv = ModelAndView()

        try:
            self.remove_context_path(request)

            for _ in range(self.configurer.max_redirect_count):
                chain = self.get_execution_chain(request)
                result = self.handle_request(chain, request, response)

                if self.process_internal_redirect(request, response):
                    continue

                # 判断是否是外部重定向
                if response.status_code in [HTTPStatus.MovedPermanently,
                                            HTTPStatus.MovedTemporarily]:
                    response.remove_headers("Content-Length", "Transfer-Encoding")
                    start_response(response.get_headline(), response.get_headers())
                    request.close()
                    response.close()
                    return [""]

                # 判断是否是 Transfer-Encoding: chunked 响应
                if isinstance(result, types.GeneratorType):
                    response.remove_headers("Content-Length")
                    # WSGI Server会自动加上 Transfer-Encoding: chunked 头
                    start_response(response.get_headline(), response.get_headers())
                    request.close()
                    response.close()
                    return result

                mv.merge(result)
                break
            else:
                raise MaxRedirectCountReached("max redirect count reached")
        except BaseException as exception:
            self.process_exception(exception, response, mv)

        body = self.rend(mv, response)
        start_response(response.get_headline(), response.get_headers())
        request.close()
        response.close()
        return [body]


if is_tornado_installed:
    __all__.append("DispatcherRequestHandler")

    from tornado.web import RequestHandler, HTTPError
    import tornado.gen as gen

    from .request_mapping_handler_mapping import \
        TornadoRequestMappingHandlerMapping
    from .handler_execution_chain import \
        TornadoHandlerExecutionChain
    from .request_mapping_handler_adapter import \
        TornadoRequestMappingHandlerAdapter


    class DispatcherRequestHandler(RequestHandler):
        def _prepare(self):
            if 'application_context' not in self.settings:
                raise HTTPError(HTTPStatus.NotFound)
            # 因为 Tornado 会为每个请求创建一个
            # RequestHandler 对象，所以，这里使用组合而非继承
            self._dispatcher = BaseDispatcher(
                self.settings["application_context"])
            if 'dispatcher_configurer' in self.settings:
                self._dispatcher.configurer = \
                    self.settings['dispatcher_configurer']
            self._dispatcher.default_handler_mapping = \
                TornadoRequestMappingHandlerMapping()
            self._dispatcher.chain_class = \
                TornadoHandlerExecutionChain
            self._dispatcher.default_handler_adapter = \
                TornadoRequestMappingHandlerAdapter()

        @gen.coroutine
        def prepare(self):
            self._prepare()

            request = Request.from_tornado_request(
                self.request,
                self.settings['application_context'])
            response = Response()
            mv = ModelAndView()

            try:
                self._dispatcher.remove_context_path(request)

                for _ in range(self._dispatcher.configurer.max_redirect_count):
                    chain = self._dispatcher.get_execution_chain(request)
                    return_value = self._dispatcher.handle_request(
                        chain,
                        request,
                        response)
                    if gen.is_future(return_value):
                        result = yield return_value
                    else:
                        result = return_value

                    if self._dispatcher.process_internal_redirect(
                            request,
                            response):
                        continue

                    # 判断是否是外部重定向
                    if response.status_code in [HTTPStatus.MovedPermanently,
                                                HTTPStatus.MovedTemporarily]:
                        response.remove_headers(
                            "Content-Length",
                            "Transfer-Encoding")
                        self.set_status(response.status_code,
                                        response.message)
                        for one_header in response.get_headers():
                            self.set_header(*one_header)
                        request.close()
                        response.close()
                        self.finish()
                        return

                    mv.merge(result)
                    break
                else:
                    raise MaxRedirectCountReached("max redirect count reached")
            except BaseException as exception:
                self._dispatcher.process_exception(exception, response, mv)

            body = self._dispatcher.rend(mv, response)
            self.set_status(response.status_code,
                            response.message)
            for one_header in response.get_headers():
                self.set_header(*one_header)
            request.close()
            response.close()
            self.finish(body)

