import os
from yosh.constants import *


def cd(args):
    if args:
       os.chdir(args[0])
    else:
       os.chdir(os.getenv('HOME'))
    return SHELL_STATUS_RUN
