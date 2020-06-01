import os
import logging

from summermvc.mvc import DispatcherApplication
from summermvc.application_context import FilePathApplicationContext

LOGGER = logging.getLogger(__name__)

PROJECT_BASE = "{{PROJECT_BASE_DIRECTORY}}"
SOURCE_ROOT = os.path.join(PROJECT_BASE, "src")
application = DispatcherApplication(
    FilePathApplicationContext(SOURCE_ROOT))


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(filename)s:%(lineno)d] %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    SERVER_PORT = {{SERVER_PORT}}
    server = make_server("0.0.0.0", SERVER_PORT, application)
    LOGGER.info("listening on 0.0.0.0:%d", SERVER_PORT)
    server.serve_forever()

