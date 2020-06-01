# coding: utf8

__all__ = ["Request", "Response"]
__authors__ = ["Tim Chow"]

from urllib import unquote, quote
from collections import namedtuple
import re
from datetime import datetime

from .exception import MissingArgumentError, InvalidRedirectURLError
from .constant import HTTPStatus
from ..utility import is_tornado_installed

protocol = namedtuple("protocol", ["scheme", "version"])

def format_header_name(header_name):
    return "-".join([w.capitalize() for w in re.split(r"[\-_]", header_name)])


class Attribute(object):
    def __init__(self):
        self._meta = {}

    def add_attribute(self, attr_name, attr_value):
        self._meta[attr_name] = attr_value

    def set_attribute(self, attr_name, attr_value):
        if attr_name in self._meta:
            self._meta[attr_name] = attr_value

    def remove_attribute(self, attr_name, default=None):
        return self._meta.pop(attr_name, default)

    def get_attribute(self, attr_name):
        return self._meta[attr_name]

    def get_attribute_or_default(self, attr_name, default=None):
        return self._meta.get(attr_name, default)

    def close(self):
        self._meta.clear()


class Request(Attribute):
    def __init__(self):
        Attribute.__init__(self)
        self._application_context = None
        self._content_length = 0
        self._body = None
        self._content_type = None
        self._content_type_attributes = {}
        self._uri = None
        self._request_method = "GET"
        self._query_string = {}
        self._user_agent = ""
        self._headers = {}
        self._cookies = {}
        self._remote_addr = "127.0.0.1"
        self._server_port = 80
        self._protocol = None

    if is_tornado_installed:
        @classmethod
        def from_tornado_request(
                cls,
                tornado_request,
                application_context):
            request = cls()

            request.application_context = application_context

            request.content_length = tornado_request \
                .headers.get("Content-Length", None)

            request.body = tornado_request.body

            content_type_string = tornado_request \
                .headers.get("Content-Type", None)
            request.content_type, \
                request.content_type_attributes = \
                    cls.parse_type_and_attributes(content_type_string)

            request.uri = tornado_request.path

            request.request_method = tornado_request.method.upper()

            request.query_string = cls.parse_query_string(
                tornado_request.query or '')

            request.user_agent = tornado_request \
                .headers.get("User-Agent")

            request.headers = dict(tornado_request.headers)

            request.cookies = dict(tornado_request.cookies)

            request.remote_addr = tornado_request.remote_ip

            host_pair = tornado_request.host.split(":", 1)
            if len(host_pair) == 1:
                request.server_port = 80
            else:
                request.server_port = int(host_pair[1])

            request.protocol = protocol(
                tornado_request.protocol.upper(),
                tornado_request.version)

            return request

    @classmethod
    def from_wsgi_environment(
            cls,
            environment,
            application_context):
        request = cls()

        request.application_context = application_context

        request.content_length = \
            int(environment.get("CONTENT_LENGTH") or 0)

        # TODO: 暂不支持 chunked 请求体
        # 读取请求体
        request.body = None
        if request.content_length:
            request.body = environment["wsgi.input"] \
                .read(request.content_length)

        content_type_string = environment.get("CONTENT_TYPE")
        request.content_type, \
            request.content_type_attributes = \
                cls.parse_type_and_attributes(content_type_string)

        request.uri = environment["PATH_INFO"]

        request.request_method = environment["REQUEST_METHOD"]

        request.query_string = cls.parse_query_string(
            environment.get("QUERY_STRING", ""))

        request.user_agent = environment.get("HTTP_USER_AGENT")

        request.headers = cls.parse_headers(environment)

        request.cookies = cls.parse_cookies(
            request.headers.pop("Cookie", ""))

        request.remote_addr = environment.get(
            "REMOTE_ADDR",
            "127.0.0.1")

        request.server_port = environment.get("SERVER_PORT", 80)

        request.protocol = protocol(
            *environment.get("SERVER_PROTOCOL",
                             "HTTP/1.0").upper().split("/", 1))

        return request

    @staticmethod
    def parse_type_and_attributes(content_type_string):
        content_type = None
        content_type_attributes = {}

        if content_type_string is not None:
            content_type_list = content_type_string.split(";")
            content_type = content_type_list[0].strip()
            for item in content_type_list[1:]:
                pair = item.strip().split("=", 1)
                if len(pair) == 2:
                    content_type_attributes[pair[0]] = pair[1]

        return content_type, content_type_attributes

    @property
    def application_context(self):
        return self._application_context

    @application_context.setter
    def application_context(self, application_context):
        self._application_context = application_context

    @property
    def content_length(self):
        return self._content_length

    @content_length.setter
    def content_length(self, content_length):
        self._content_length = content_length

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        self._body = body

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, content_type):
        self._content_type = content_type

    @property
    def content_type_attributes(self):
        return self._content_type_attributes

    @content_type_attributes.setter
    def content_type_attributes(self, content_type_attributes):
        self._content_type_attributes = content_type_attributes

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        if not uri.startswith("/"):
            raise InvalidRedirectURLError("invalid uri")
        self._uri = uri

    @property
    def request_method(self):
        return self._request_method

    @request_method.setter
    def request_method(self, request_method):
        self._request_method = request_method

    @property
    def query_string(self):
        return self._query_string

    @query_string.setter
    def query_string(self, query_string):
        self._query_string = query_string

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self._user_agent = user_agent

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        self._cookies = cookies

    @property
    def remote_addr(self):
        return self._remote_addr

    @remote_addr.setter
    def remote_addr(self, remote_addr):
        self._remote_addr = remote_addr

    @property
    def server_port(self):
        return self._server_port

    @server_port.setter
    def server_port(self, server_port):
        self._server_port = server_port

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = protocol

    @staticmethod
    def parse_query_string(query_string):
        d = {}
        for item in query_string.split("&"):
            pair = item.split("=", 1)
            if len(pair) == 2:
                d.setdefault(unquote(pair[0]), []) \
                    .append(unquote(pair[1]))
        return d

    def get_argument(self, argument):
        if argument not in self._query_string:
            raise MissingArgumentError("no argument named %s" % argument)
        return self._query_string[argument][0]

    def get_arguments(self, argument):
        if argument not in self._query_string:
            raise MissingArgumentError("no argument named %s" % argument)
        return self._query_string[argument]

    def add_argument(self, arg_name, arg_value):
        self._query_string.setdefault(
            quote(arg_name), []).append(quote(arg_value))

    @staticmethod
    def parse_headers(environment):
        headers = {}
        for key, value in environment.iteritems():
            if not key.startswith("HTTP_"):
                continue
            header_name = format_header_name(key[5:])
            headers[header_name] = value
        return headers

    @staticmethod
    def parse_cookies(cookie_string):
        cookies = {}
        for item in cookie_string.split(";"):
            pair = item.strip().split("=", 1)
            if len(pair) == 1:
                cookies[unquote(pair[0].strip())] = ""
            else:
                cookies[unquote(pair[0].strip())] = \
                    unquote(pair[1].strip())
        return cookies

    def get_header(self, header_name):
        return self.headers[format_header_name(header_name)]

    def get_header_or_default(self, header_name, default=None):
        return self.headers.get(
            format_header_name(header_name), default)

    def get_cookie(self, cookie_name):
        return self.cookies[cookie_name]

    def get_cookie_or_default(self, cookie_name, default=None):
        return self.cookies.get(cookie_name, default)

    def close(self):
        del self._application_context
        Attribute.close(self)


class Response(object):
    def __init__(self):
        self._initialize()

    def _initialize(self):
        self._status_code = 200
        self._message = "OK"
        self._headers = {}
        self._cookies = {}
        self._internal_redirect_to = None

    def set_status(self, status_code, reason=None):
        self._status_code = status_code
        self._message = reason or HTTPStatus.get_message(status_code)

    def add_header(self, header_name, header_value):
        self._headers[format_header_name(header_name)] = header_value

    def redirect(self, url, permanently=True):
        if url.startswith("http://") or \
                url.startswith("https://"):
            self.add_header("Location", url)
            if permanently:
                self.set_status(HTTPStatus.MovedPermanently)
            else:
                self.set_status(HTTPStatus.MovedTemporarily)
        elif url.startswith("/"):
            self._internal_redirect_to = url
        else:
            raise InvalidRedirectURLError("invalid redirect url")

    def set_cookie(self, key, value, path=None, domain=None,
                   expires=None, secure=False, http_only=False):
        cookie = ["%s=%s"%(quote(key), quote(value))]
        if path is not None:
            cookie.append("Path=%s" % path)
        if domain is not None:
            cookie.append("Domain=%s" % domain)
        if isinstance(expires, datetime):
            cookie.append("Expires=%s" %
                          expires.strftime("%a, %d %b %Y %H:%M:%S GMT"))
        if secure:
            cookie.append("Secure")
        if http_only:
            cookie.append("HttpOnly")
        self._cookies[key] = "; ".join(cookie)

    def get_headline(self):
        return "%d %s" % (self._status_code, self._message)

    def get_headers(self):
        headers = self._headers.items()
        for key in self._cookies:
            headers.append(("Set-Cookie", self._cookies[key]))
        return headers

    @property
    def status_code(self):
        return self._status_code

    @property
    def message(self):
        return self._message

    def get_header(self, header_name):
        header_name = format_header_name(header_name)
        return self._headers.get(header_name, None)

    def remove_header(self, header_name):
        header_name = format_header_name(header_name)
        self._headers.pop(header_name, None)

    def remove_headers(self, *header_names):
        for header_name in header_names:
            self.remove_header(header_name)

    def close(self):
        pass

    @property
    def internal_redirect_to(self):
        return self._internal_redirect_to

    def clear(self):
        self._initialize()

