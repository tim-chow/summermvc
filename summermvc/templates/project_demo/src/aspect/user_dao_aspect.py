# coding: utf8

import logging
import functools
import time

from summermvc.decorator import *

LOGGER = logging.getLogger(__name__)


@component
@aspect(1)
class UserDaoAspect(object):
    @around(r"UserDao .*")
    def around_before(self):
        return functools.partial(
            self.around_after, time.time())

    @staticmethod
    def around_after(start_time,
                     jp,
                     returning,
                     exc_info):
        LOGGER.info(
            "method: %s is called with "
            "args: %s, keyword args: %s used %.3fs",
            jp.method, jp.args, jp.kwargs,
            time.time()-start_time)
