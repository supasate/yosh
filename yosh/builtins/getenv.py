import os
from yosh.constants import *


def getenv(args):
    print os.getenv(args[0])
    return SHELL_STATUS_RUN
