# coding: utf8

import json
from summermvc.decorator import *
from summermvc.mvc import *


@component
class MultiViewResolver(ViewResolver):
    @post_construct
    def setup(self):
        self._json_view = JsonView()

    @override
    def get_view(self, view_name, status_code):
        return self._json_view


class JsonView(View):
    @override
    def render(self, model):
        return json.dumps(model, default=self._default)

    def _default(self, obj):
        if isinstance(obj, Model):
            return obj.as_map()
        raise TypeError("%r is not JSON Serializable", obj)

    @override
    def get_content_type(self):
        return "application/json; charset=UTF-8"
