# coding: utf8

import logging

from summermvc.decorator import *
from summermvc.mvc import HTTPStatus

LOGGER = logging.getLogger(__name__)


# 使用 rest_controller 装饰器
@rest_controller
class UserController(object):
    @auto_wired
    def _user_service(self):
        pass

    # 后置构造方法
    @post_construct
    def setup(self):
        LOGGER.info("user controller is constructed")

    # 前置析构方法
    @pre_destroy
    def teardown(self):
        LOGGER.info("user controller will be destroyed")

    @request_mapping("/get/user")
    def get_user_1(self, arg_user_id, model, arg_format="json"):
        data = self._user_service.get_user_by_id(arg_user_id)
        model.add_attribute("user_info", data)
        return arg_format

    @request_mapping(r"/get/user/(\d+)")
    def get_user_2(self):
        raise ValueError("just for test exception handler")

    @exception_handler(r"/get/user/(\d+)", ValueError)
    def handle_runtime_error(self, model, response, arg_format="json"):
        response.set_status(HTTPStatus.InternalError)
        model.add_attribute("exception_happened", True)
        return arg_format
