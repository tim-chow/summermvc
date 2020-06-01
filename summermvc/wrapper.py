# coding: utf8

__all__ = ["wrapper"]
__authors__ = ["Tim Chow"]

from functools import wraps
import inspect
import sys
import types

from .joint_point import JointPoint
from .exception import Return
from .utility import is_tornado_installed


def wrapper(
        before_advices,
        around_advices,
        after_returning_advices,
        after_throwing_advices,
        after_advices):
    def _inner(f):
        @wraps(f)
        def _real_logic(*a, **kw):
            jp = JointPoint(f, a, kw)
            # 执行前置通知
            for before_advice in before_advices:
                formal_arguments = inspect.getargspec(before_advice).args
                try:
                    if "joint_point" in formal_arguments:
                        before_advice(joint_point=jp)
                    else:
                        before_advice()
                except Return as e:
                    return e.get_return_value()

            # 执行环绕通知
            around_after_advices = []
            for around_advice in around_advices:
                formal_arguments = inspect.getargspec(around_advice).args
                try:
                    if "joint_point" in formal_arguments:
                        result = around_advice(joint_point=jp)
                    else:
                        result = around_advice()
                    if callable(result):
                        around_after_advices.append(result)
                except Return as e:
                    return e.get_return_value()

            # 执行连接点
            returning = None
            exc_info = None
            try:
                returning = jp.proceed()
            except:
                exc_info = sys.exc_info()

            # 执行环绕通知
            for around_after_advice in around_after_advices:
                try:
                    around_after_advice(jp, returning, exc_info)
                except Return as e:
                    return e.get_return_value()

            if exc_info is None:
                # 执行返回通知
                for after_returning_advice in after_returning_advices:
                    formal_arguments = inspect.getargspec(after_returning_advice).args
                    kwargs = {}
                    if "joint_point" in formal_arguments:
                        kwargs["joint_point"] = jp
                    if "returning" in formal_arguments:
                        kwargs["returning"] = returning
                    try:
                        after_returning_advice(**kwargs)
                    except Return as e:
                        return e.get_return_value()
            else:
                # 执行异常通知
                for after_throwing_advice in after_throwing_advices:
                    formal_arguments = inspect.getargspec(after_throwing_advice).args
                    kwargs = {}
                    if "joint_point" in formal_arguments:
                        kwargs["joint_point"] = jp
                    if "exc_info" in formal_arguments:
                        kwargs["exc_info"] = exc_info
                    try:
                        after_throwing_advice(**kwargs)
                    except Return as e:
                        return e.get_return_value()

            # 执行最终通知
            for after_advice in after_advices:
                formal_arguments = inspect.getargspec(after_advice).args
                kwargs = {}
                if "joint_point" in formal_arguments:
                    kwargs["joint_point"] = jp
                if "returning" in formal_arguments:
                    kwargs["returning"] = returning
                if "exc_info" in formal_arguments:
                    kwargs["exc_info"] = exc_info
                try:
                    after_advice(**kwargs)
                except Return as e:
                    return e.get_return_value()

            if exc_info is not None:
                raise exc_info[0], exc_info[1], exc_info[2]
            return returning
        return _real_logic
    return _inner


if is_tornado_installed:
    __all__.append("tornado_wrapper")

    import tornado.gen as gen


    def tornado_wrapper(
            before_advices,
            around_advices,
            after_returning_advices,
            after_throwing_advices,
            after_advices):
        def _inner(f):
            if not gen.is_coroutine_function(f):
                return wrapper(
                    before_advices,
                    around_advices,
                    after_returning_advices,
                    after_throwing_advices,
                    after_advices)(f)

            @gen.coroutine
            @wraps(f)
            def _real_logic(*a, **kw):
                jp = JointPoint(f, a, kw)
                # 执行前置通知
                for before_advice in before_advices:
                    formal_arguments = inspect.getargspec(before_advice).args
                    try:
                        if "joint_point" in formal_arguments:
                            return_value = before_advice(joint_point=jp)
                        else:
                            return_value = before_advice()
                        if gen.is_future(return_value):
                            yield return_value
                    except Return as e:
                        raise gen.Return(e.get_return_value())

                # 执行环绕通知
                around_after_advices = []
                for around_advice in around_advices:
                    formal_arguments = inspect.getargspec(around_advice).args
                    try:
                        if "joint_point" in formal_arguments:
                            return_value = around_advice(joint_point=jp)
                        else:
                            return_value = around_advice()
                        if gen.is_future(return_value):
                            result = yield return_value
                        else:
                            result = return_value
                        if callable(result):
                            around_after_advices.append(result)
                    except Return as e:
                        raise gen.Return(e.get_return_value())

                # 执行连接点
                returning = None
                exc_info = None
                try:
                    returning = jp.proceed()
                    if gen.is_future(returning):
                        returning = yield returning
                except:
                    exc_info = sys.exc_info()

                # 执行环绕通知
                for around_after_advice in around_after_advices:
                    try:
                        return_value = around_after_advice(jp, returning, exc_info)
                        if gen.is_future(return_value):
                            yield return_value
                    except Return as e:
                        raise gen.Return(e.get_return_value())

                if exc_info is None:
                    # 执行返回通知
                    for after_returning_advice in after_returning_advices:
                        formal_arguments = inspect.getargspec(after_returning_advice).args
                        kwargs = {}
                        if "joint_point" in formal_arguments:
                            kwargs["joint_point"] = jp
                        if "returning" in formal_arguments:
                            kwargs["returning"] = returning
                        try:
                            return_value = after_returning_advice(**kwargs)
                            if gen.is_future(return_value):
                                yield return_value
                        except Return as e:
                            raise gen.Return(e.get_return_value())
                else:
                    # 执行异常通知
                    for after_throwing_advice in after_throwing_advices:
                        formal_arguments = inspect.getargspec(after_throwing_advice).args
                        kwargs = {}
                        if "joint_point" in formal_arguments:
                            kwargs["joint_point"] = jp
                        if "exc_info" in formal_arguments:
                            kwargs["exc_info"] = exc_info
                        try:
                            return_value = after_throwing_advice(**kwargs)
                            if gen.is_future(return_value):
                                yield return_value
                        except Return as e:
                            raise gen.Return(e.get_return_value())

                # 执行最终通知
                for after_advice in after_advices:
                    formal_arguments = inspect.getargspec(after_advice).args
                    kwargs = {}
                    if "joint_point" in formal_arguments:
                        kwargs["joint_point"] = jp
                    if "returning" in formal_arguments:
                        kwargs["returning"] = returning
                    if "exc_info" in formal_arguments:
                        kwargs["exc_info"] = exc_info
                    try:
                        return_value = after_advice(**kwargs)
                        if gen.is_future(return_value):
                            yield return_value
                    except Return as e:
                        raise gen.Return(e.get_return_value())

                if exc_info is not None:
                    raise exc_info[0], exc_info[1], exc_info[2]
                raise gen.Return(returning)
            return _real_logic
        return _inner

