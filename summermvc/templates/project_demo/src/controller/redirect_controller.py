# coding: utf8

from summermvc.decorator import *


@rest_controller
class RedirectController(object):
    @request_mapping("/redirect")
    def redirect(self, response):
        response.redirect("http://timd.cn/")

    @request_mapping("/internal/redirect")
    def internal_redirect(self, response):
        response.redirect("/test-internal-redirect")

    @request_mapping("/test-internal-redirect")
    def test_internal_redirect(self, model, arg_format="json"):
        model.add_attribute("info", "this is an internal redirect")
        return arg_format
