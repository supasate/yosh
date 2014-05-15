import os
from yosh.constants import *


def export(args):
    var=args[0].split('=', 1 );
    os.environ[var[0]] = var[1]
    return SHELL_STATUS_RUN
