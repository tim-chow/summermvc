# coding: utf8

from summermvc.decorator import *


@rest_controller
class ChunkController(object):
    @request_mapping("/chunk", produce="text/plain")
    def test_chunk(self):
        for i in range(3):
            yield "this is %3d.\n" % i

        yield help_func()
