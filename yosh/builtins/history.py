import os
import sys
from yosh.constants import *


def history(args):
    with open(HISTORY_PATH, 'r') as history_file:
        lines = history_file.readlines()

        # default limit is whole file
        limit = len(lines)

        if len(args) > 0:
            limit = int(args[0])

        # start history line to print out
        start = len(lines) - limit

        for line_num, line in enumerate(lines):
            if line_num >= start:
                sys.stdout.write('%d %s' % (line_num + 1, line))
        sys.stdout.flush()

    return SHELL_STATUS_RUN
