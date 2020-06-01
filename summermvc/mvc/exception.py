# coding: utf8

__authors__ = ["TimChow"]


# 所有异常的基类
class MVCError(StandardError):
    pass


# 请求的查询字符串中缺少必要的参数
class MissingArgumentError(MVCError):
    pass


# handler 定义了不被支持的参数
class InvalidArgumentError(MVCError):
    pass


# handler 返回了不被支持的值
class InvalidReturnValueError(MVCError):
    pass


# 外部重定向时，URL 必须以 http:// 或 https:// 开头
class InvalidRedirectURLError(MVCError):
    pass


# 当拦截器抛出该异常时，请求不会向后面继续传递
class InterceptError(MVCError):
    pass


# 找不到 handler
class NoHandlerFoundError(MVCError):
    pass


# 找不到适配器
class NoAdapterFoundError(MVCError):
    pass


# 未知的请求方法
class UnsupportedRequestMethodError(MVCError):
    pass


# 达到了最大的内部重定向次数
class MaxRedirectCountReached(MVCError):
    pass
