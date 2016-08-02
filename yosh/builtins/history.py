import os
from yosh.constants import *


def history(args):
    history_path = os.getenv('HOME') + '/.yosh_history'

    with open(history_path) as history_file:
        lines = history_file.readlines()
        # default limit is whole file
        limit = len(lines)

        if len(args) > 0:
            limit = int(args[0])

        # start history line to print out
        start = len(lines) - limit

        for line_num, line in enumerate(lines):
            if line_num >= start:
                output = str(line_num + 1) + " " + line
                print(output.strip())
    return SHELL_STATUS_RUN
