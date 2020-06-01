# coding: utf8

__all__ = ["JointPoint"]
__authors__ = ["Tim Chow"]

import inspect


class JointPoint(object):
    """连接点对象"""
    def __init__(self, method=None, args=None, kwargs=None):
        self._method = method
        self._args = args or tuple()
        self._kwargs = kwargs or dict()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        assert callable(method), "method must be callable"
        self._method = method

    def get_signature(self):
        if self.method is None:
            return None
        arg_spec = inspect.getargspec(self.method)
        return arg_spec.args, arg_spec.varargs, arg_spec.keywords

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        assert isinstance(args, tuple), "tuple expected"
        self._args = args

    @property
    def kwargs(self):
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs):
        assert isinstance(kwargs, dict), "dict expected"
        self._kwargs = kwargs

    def get_arguments(self):
        if self.method is None:
            raise RuntimeError("no method was specified")

        bind_result = {}
        arg_spec = inspect.getargspec(self.method)
        # 形参列表
        formal_arguments = arg_spec.args
        # 默认参数
        if arg_spec.defaults is not None:
            defaults = dict(zip(
                formal_arguments[-1*len(arg_spec.defaults):],
                arg_spec.defaults))
        else:
            defaults = dict()

        # 实参列表
        actual_arguments = list(self.args)
        # 关键字参数
        keyword_arguments = self.kwargs

        # 实际参数的数量大于形式参数的数量
        if len(actual_arguments) > len(formal_arguments):
            # 如果没定义变长参数，则抛出异常
            if arg_spec.varargs is None:
                raise ValueError("too many arguments")
            bind_result.update(
                dict(
                    zip(formal_arguments,
                        actual_arguments[:len(formal_arguments)]
                    )
                )
            )
            bind_result[arg_spec.varargs] = tuple(actual_arguments[len(formal_arguments):])
            if arg_spec.keywords is not None:
                for keyword_argument in keyword_arguments:
                    if keyword_argument in formal_arguments:
                        raise ValueError("multiple value for argument %s" % keyword_argument)
                bind_result[arg_spec.keywords] = keyword_arguments
            elif keyword_arguments:
                raise ValueError("there are no keyword arguments")
        # 实际参数的数量小于等于形式参数的数量
        else:
            if arg_spec.varargs is not None:
                bind_result[arg_spec.varargs] = tuple()
            bind_result.update(dict(zip(
                formal_arguments[:len(actual_arguments)],
                actual_arguments)))
            for formal_argument in formal_arguments[len(actual_arguments):]:
                if formal_argument in keyword_arguments:
                    bind_result[formal_argument] = keyword_arguments.pop(formal_argument)
                    continue
                if formal_argument not in defaults:
                    raise ValueError("missing argument %s" % formal_argument)
                bind_result[formal_argument] = defaults[formal_argument]
            if arg_spec.keywords is not None:
                for keyword_argument in keyword_arguments:
                    if keyword_argument in formal_arguments[:len(actual_arguments)]:
                        raise ValueError("multiple value for argument %s" % keyword_argument)
                bind_result[arg_spec.keywords] = keyword_arguments
            elif keyword_arguments:
                raise ValueError("there are no keyword arguments")
        return bind_result

    def proceed(self):
        if self.method is None:
            raise RuntimeError("no method specified")
        return self.method(*self.args, **self.kwargs)
