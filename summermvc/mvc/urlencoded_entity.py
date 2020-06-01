# coding: utf8

__all__ = ["URLEncodedEntityParser"]
__authors__ = ["Tim Chow"]

from urllib import unquote

from .exception import MissingArgumentError


class URLEncodedEntityParser(object):
    def __init__(self, body):
        self._arguments = self.parse(body)

    @staticmethod
    def parse(body):
        arguments = {}
        for item in body.split("&"):
            pair = item.split("=", 1)
            if len(pair) != 2:
                continue
            arguments.setdefault(unquote(pair[0]), []).append(unquote(pair[1]))
        return arguments

    def get_argument(self, argument):
        if argument not in self._arguments:
            raise MissingArgumentError("missing argument %s" % argument)
        return self._arguments[argument][0]

    def get_arguments(self, argument):
        if argument not in self._arguments:
            raise MissingArgumentError("missing argument %s" % argument)
        return self._arguments[argument]
