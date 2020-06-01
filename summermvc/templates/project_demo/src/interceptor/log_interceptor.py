# coding: utf8

import logging

from summermvc.mvc import HandlerInterceptor
from summermvc.decorator import *

LOGGER = logging.getLogger(__name__)


@component
class LogInterceptor(HandlerInterceptor):
    @override
    def pre_handle(self, request, response, model_and_view):
        logging.info("pre handle in LogInterceptor")

    @override
    def post_handle(self, request, response, model_and_view):
        logging.info("post handle in LogInterceptor")

    @override
    def path_pattern(self):
        return r"/.*"

    @override
    def get_order(self):
        return 1
