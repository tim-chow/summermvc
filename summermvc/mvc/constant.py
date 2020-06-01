# coding: utf8

__all__ = ["RequestMethod", "HTTPStatus"]
__authors__ = ["Tim Chow"]

from .exception import UnsupportedRequestMethodError


class RequestMethod(object):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"

    @classmethod
    def from_string(cls, string):
        for attr_name, attr_value in vars(cls).iteritems():
            if not isinstance(attr_value, basestring):
                continue
            if attr_value == string.upper():
                return getattr(cls, attr_name)
        raise UnsupportedRequestMethodError("unsupported request method")


class HTTPStatus(object):
    Continue = 100

    OK = 200

    MovedPermanently = 301
    MovedTemporarily = 302
    NotModified = 304
    
    BadRequest = 400
    Unauthorized = 401
    Forbidden = 403
    NotFound = 404 
    MethodNotAllowed = 405

    InternalError = 500
    BadGateway = 502
    NotAvailableTemporarily = 503
    GatewayTimeout = 504

    @classmethod
    def get_message(cls, code, default=None):
        for attr_name, attr_value in vars(cls).iteritems():
            if not isinstance(attr_value, int):
                continue
            if attr_value == code:
                return attr_name
        return default or "Unknown"
