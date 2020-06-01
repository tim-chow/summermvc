# coding: utf8

import logging

from summermvc.decorator import *
from summermvc.mvc import *

LOGGER = logging.getLogger(__name__)


@rest_controller
class MultipartController(object):
    @request_mapping("/upload",
                     method=RequestMethod.GET,
                     produce="text/html")
    def upload_files_get(self):
        html = """
            <html>
                <head>
                    <title>multipart test</title>
                </head>

                <body>
                    <form action="/upload" enctype="multipart/form-data" method="post">
                        <input type="file" name="upload_file_1" /><br />
                        <input type="file" name="upload_file_2" /><br />
                        <input type="submit" value="submit" /><br />
                    </form>
                <body>
            </html>
            """.strip()
        yield html

    @request_mapping("/upload", method=RequestMethod.POST)
    def upload_files_post(self, model, request, request_body):
        uploaded_files = MultipartParser(
            request_body,
            request.content_type_attributes["boundary"]).files
        LOGGER.debug("uploaded files are: %s", uploaded_files)
        model.add_attribute("success", True)
        return "json"
