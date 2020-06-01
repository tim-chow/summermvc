# coding: utf8

from summermvc.decorator import configuration
from summermvc.field import ValueField


@configuration
class DBConfiguration(object):
    host = ValueField("127.0.0.1")
    port = ValueField(3306)

    def __str__(self):
        return "%s{host=%s, port=%d}" % (
            self.__class__.__name__,
            self.host,
            self.port)
