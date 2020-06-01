# coding: utf8

from summermvc.decorator import builtin


# 使用 builtin 装饰器的顶级类或方法，会被导入到内建命名空间，
# + 因此，可以直接使用
@builtin
def help_func():
    return "I am help func."
