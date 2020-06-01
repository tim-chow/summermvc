# coding: utf8

import logging

from summermvc.decorator import *
from summermvc.field import *

LOGGER = logging.getLogger(__name__)


@repository
class UserDao(object):
    configuration = AutoWiredField("DBConfiguration")

    @post_construct
    def setup(self):
        LOGGER.info("user dao is constructed with %s",
                    self.configuration)

    @pre_destroy
    def teardown(self):
        LOGGER.info("user dao is destroyed")

    def get_user_by_id(self, user_id):
        return {"user_id": user_id, "name": "Tim Chow"}
