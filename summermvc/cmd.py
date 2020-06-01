# coding: utf8

__all__ = ["DispatchCommand"]
__authors__ = ["Tim Chow"]

from optparse import OptionParser
import sys
import os
import shutil

from pkg_resources import resource_filename


class DispatchCommand(object):
    def __init__(self, sub_command, options):
        self._sub_command = sub_command
        self._options = options

    def _sub_command__project(self):
        src = resource_filename("summermvc", "templates/project_demo")
        dst = self._options.name
        print("\033[32mcreating project\033[0m")
        if os.path.exists(dst):
            sys.exit("\033[31m%s already exists\033[0m" % dst)
        dst = os.path.abspath(dst)
        print("\033[32mcopying files\033[0m")
        shutil.copytree(src, dst)
        print("\033[32mdeleting .pyc/.pyo \033[0m")
        # 清除.pyc、.pyo文件
        for base_directory, _, file_names in os.walk(dst):
            for file_name in file_names:
                file_name = os.path.join(base_directory, file_name)
                if os.path.splitext(file_name)[1] in [".pyc", ".pyo"]:
                    os.remove(file_name)

        # 替换application.py中的宏
        server_port = str(self._options.server_port or 8081)
        application_path = os.path.join(dst, "application.py")
        if os.path.isfile(application_path):
            with open(application_path, "rb") as fd:
                content = fd.read() \
                    .replace("{{PROJECT_BASE_DIRECTORY}}", dst) \
                    .replace("{{SERVER_PORT}}", server_port)
            with open(application_path, "wb") as fd:
                fd.write(content)
        print("\033[32mproject is created successfully\033[0m")
        return 0

    @staticmethod
    def line_count(file_name):
        count = 0
        with open(file_name) as fd:
            for _ in fd:
                count = count + 1
        return count

    def _sub_command__line_count(self):
        # 不统计的文件的扩展名
        exclude_pattern = self._options.exclude_pattern or ""
        exclude_patterns = exclude_pattern.replace(" ", "").split(",")
        exclude_patterns = [(".%s" % e) for e in exclude_patterns]

        base_directory = self._options.base_directory
        if not base_directory:
            sys.exit("\033[31mno base directory or file provided\033[0m")
        if not os.path.exists(base_directory):
            sys.exit("\033[31m%s not exists\033[0m" % base_directory)
        if os.path.isfile(base_directory):
            if os.path.splitext(base_directory)[1] in exclude_patterns:
                sys.exit("\033[32mskipped %s\033[0m" % base_directory)
            sys.exit("\033[32m[%s] [%d]\033[0m" % (
                base_directory,
                self.line_count(base_directory)))

        total_count = 0
        for dir_name, _, file_names in os.walk(base_directory):
            for file_name in file_names:
                file_name = os.path.join(dir_name, file_name)
                if os.path.splitext(file_name)[1] in exclude_patterns:
                    print("\033[32mskipped %s\033[0m" % file_name)
                    continue
                count = self.line_count(file_name)
                print("\033[32m[%s] [%d]\033[0m" % (file_name, count))
                total_count = total_count + count
        print("\033[32mtotal count: [%d]\033[0m" % total_count)
        return 0

    def run(self):
        f = getattr(self, "_sub_command__%s" % self._sub_command, None)
        if f is None:
            sys.exit("\033[31mthere is no subcommand named %s\033[0m" % self._sub_command)
        return f() or 0


def main(args=None):
    parser = OptionParser(usage="%prog subcommand [options]")
    parser.add_option("-n",
                      "--name",
                      default="summermvc_demo",
                      type=str,
                      dest="name",
                      help="project name")
    parser.add_option("-d",
                      "--directory",
                      type=str,
                      dest="base_directory",
                      help="base directory or file")
    parser.add_option("-e",
                      "--exclude",
                      type=str,
                      dest="exclude_pattern",
                      help="exclude pattern")
    parser.add_option("-p",
                      "--port",
                      type=int,
                      dest="server_port",
                      help="server port")

    options, args = parser.parse_args(args or sys.argv[1:])
    if len(args) < 1:
        parser.error("no subcommand provided")

    dispatch_command = DispatchCommand(args[0], options)
    return dispatch_command.run()
