from .scanner import *
from .exception import *
from .bean import *
from .bean_factory import *
from .application_context import *
from .joint_point import *


def return_value(value):
    raise Return(value)
