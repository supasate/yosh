import os
from yosh.constants import *


def history(args):
    count = 0
    if args:
        count = int(args[0]) + 1
    file = open(os.getenv("HOME") + "/.shistory")
    lines = file.readlines()
    for i, el in enumerate(lines):
        if count != 0:
            if len(lines) - count < i < len(lines):
                output = str(i) + " " + el
                print (output.strip())
        else:
            output = str(i) + " " + el
            print (output.strip())
    return SHELL_STATUS_RUN
