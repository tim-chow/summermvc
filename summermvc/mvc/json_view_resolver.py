# coding: utf8

__all__ = ["JsonViewResolver"]
__authors__ = ["Tim Chow"]

import json
import datetime

from .interface import ViewResolver, View
from .model_and_view import Model


class JsonView(View):
    def get_content_type(self):
        return "application/json; charset=UTF-8"

    def render(self, model):
        return self.__dumps(model)

    def __dumps(self, model):
        return json.dumps(model, default=self.__default)

    def __default(self, obj):
        if isinstance(obj, Model):
            return obj.as_map()
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, datetime.time):
            return obj.strftime("%H:%M:%S")
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError("%r is not JSON serializable" % obj)


class JsonViewResolver(ViewResolver):
    def __init__(self):
        self._json_view = JsonView()

    def get_view(self, view_name, status_code):
        return self._json_view
