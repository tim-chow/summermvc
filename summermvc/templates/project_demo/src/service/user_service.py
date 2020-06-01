# coding: utf8

import logging

from summermvc.decorator import *

LOGGER = logging.getLogger(__name__)


@service
class UserService(object):
    @post_construct
    def setup(self):
        LOGGER.info("user service is constructed")

    @auto_wired
    def _user_dao(self):
        pass

    def get_user_by_id(self, user_id):
        return self._user_dao.get_user_by_id(user_id)
