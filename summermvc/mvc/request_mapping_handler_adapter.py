# coding: utf8

__all__ = ["RequestMappingHandlerAdapter"]
__authors__ = ["Tim Chow"]

import inspect
import types

from .interface import HandlerAdapter
from ..decorator import *
from .exception import *
from .model_and_view import ModelAndView, Model
from ..utility import is_tornado_installed


class RequestMappingHandlerAdapter(HandlerAdapter):
    def supports(self, handler):
        return is_request_mapping_present(handler.page_handler)

    @staticmethod
    def build_args(arg_spec, request, response, mv, matches, exc=None):
        args = arg_spec.args
        defaults = {}
        if arg_spec.defaults:
            defaults = dict(zip(
                arg_spec.args[-1 * len(arg_spec.defaults):],
                arg_spec.defaults))

        bind_args = []
        for arg_name in args[1:]:
            if arg_name.startswith("arg_"):
                if len(arg_name) == 4:
                    raise InvalidArgumentError("missing argument name")
                try:
                    bind_args.append(request.get_argument(arg_name[4:]))
                except MissingArgumentError:
                    if arg_name not in defaults:
                        raise
                    bind_args.append(defaults[arg_name])
                continue

            if arg_name.startswith("args_"):
                if len(arg_name) == 5:
                    raise InvalidArgumentError("missing argument name")
                try:
                    bind_args.append(request.get_arguments(arg_name[5:]))
                except MissingArgumentError:
                    if arg_name not in defaults:
                        raise
                    bind_args.append(defaults[arg_name])
                continue

            if arg_name == "request":
                bind_args.append(request)
                continue

            if arg_name == "request_body":
                bind_args.append(request.body)
                continue

            if arg_name == "response":
                bind_args.append(response)
                continue

            if arg_name == "model_and_view":
                bind_args.append(mv)
                continue

            if arg_name == "model":
                bind_args.append(mv.model)
                continue

            if arg_name.startswith("path_var_"):
                if len(arg_name) == 9:
                    raise InvalidArgumentError("missing path variable name")
                if arg_name[9:] in matches:
                    bind_args.append(matches[arg_name[9:]])
                elif arg_name in defaults:
                    bind_args.append(defaults[arg_name])
                else:
                    raise MissingArgumentError("missing argument %s" % arg_name)
                continue

            if arg_name.startswith("header_"):
                if len(arg_name) == 7:
                    raise InvalidArgumentError("missing header name")
                header = request.get_header_or_default(arg_name[7:], None)
                if header is not None:
                    bind_args.append(header)
                elif arg_name in defaults:
                    bind_args.append(defaults[arg_name])
                else:
                    raise MissingArgumentError("missing argument %s" % arg_name)
                continue

            if arg_name.startswith("cookie_"):
                if len(arg_name) == 7:
                    raise InvalidArgumentError("missing cookie name")
                cookie = request.get_cookie_or_default(arg_name[7:], None)
                if cookie is not None:
                    bind_args.append(cookie)
                elif arg_name in defaults:
                    bind_args.append(defaults[arg_name])
                else:
                    raise MissingArgumentError("missing argument %s" % arg_name)
                continue

            if arg_name == "exc":
                bind_args.append(exc)
                continue

            raise InvalidArgumentError("unsupported argument %s" % arg_name)
        return tuple(bind_args)

    def handle(self, request, response, handler_execution_chain):
        mv = ModelAndView()
        handler = handler_execution_chain.handler
        exceptions = tuple(handler.exception_handlers.keys())
        try:
            arg_spec = get_request_mapping(
                handler.page_handler)["arg_spec"]
            result = handler_execution_chain.handle(
                request,
                response,
                mv,
                *self.build_args(
                    arg_spec,
                    request,
                    response,
                    mv,
                    handler.matches))
        except exceptions as exc:
            for exception in exceptions:
                if isinstance(exc, exception):
                    exception_handler, matches = \
                        handler.exception_handlers[exception]
                    arg_spec = get_exception_handler(
                        exception_handler)["arg_spec"]
                    result = exception_handler(
                        *self.build_args(
                            arg_spec,
                            request,
                            response,
                            mv,
                            matches,
                            exc))
                    break
            else:
                raise RuntimeError("unreachable")

        return self.post_handle(
            response,
            handler,
            result,
            mv)

    @staticmethod
    def post_handle(response,
                    handler,
                    result,
                    mv,
                    allow_generator=True):
        # 设置 Content-Type
        if response.get_header("Content-Type") is None:
            rm = get_request_mapping(handler.page_handler)
            if rm["produce"] is not None:
                response.add_header("Content-Type", rm["produce"])

        if isinstance(result, types.GeneratorType):
            if allow_generator:
                return result
            raise InvalidReturnValueError("invalid return value")

        if result is None:
            pass
        elif isinstance(result, Model):
            mv.model.merge(result)
        elif isinstance(result, ModelAndView):
            mv.merge(result)
        elif isinstance(result, basestring):
            mv.view = result
        else:
            raise InvalidReturnValueError("invalid return value")
        return mv


if is_tornado_installed:
    __all__.append("TornadoRequestMappingHandlerAdapter")

    import tornado.gen as gen


    class TornadoRequestMappingHandlerAdapter(
            RequestMappingHandlerAdapter):
        @gen.coroutine
        def handle(self,
                   request,
                   response,
                   handler_execution_chain):
            mv = ModelAndView()
            handler = handler_execution_chain.handler
            exceptions = tuple(handler.exception_handlers.keys())
            try:
                arg_spec = get_request_mapping(
                    handler.page_handler)["arg_spec"]
                return_value = handler_execution_chain.handle(
                    request,
                    response,
                    mv,
                    *self.build_args(
                        arg_spec,
                        request,
                        response,
                        mv,
                        handler.matches))
                if gen.is_future(return_value):
                    result = yield return_value
                else:
                    result = return_value
            except exceptions as exc:
                for exception in exceptions:
                    if isinstance(exc, exception):
                        exception_handler, matches = \
                            handler.exception_handlers[exception]
                        arg_spec = get_exception_handler(
                            exception_handler)["arg_spec"]
                        return_value = exception_handler(
                            request,
                            response,
                            mv,
                            *self.build_args(
                                arg_spec,
                                request,
                                response,
                                mv,
                                matches,
                                exc))
                        if gen.is_future(return_value):
                            result = yield return_value
                        else:
                            result = return_value
                        break
                else:
                    raise RuntimeError("unreachable")

            mv = self.post_handle(response, handler, result, mv, False)
            raise gen.Return(mv)

