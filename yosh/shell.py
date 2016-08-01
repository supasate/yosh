import os
import sys
import shlex
import getpass
import socket
import signal
import subprocess
import platform
from yosh.constants import *
from yosh.builtins import *

# Hash map to store built-in function name and reference as key and value
built_in_cmds = {}


def tokenize(string):
    token = shlex.split(string)
    for i, el in enumerate(token):
        if el.startswith('$'):
            token[i] = os.getenv(token[i][1:])
    return token


def handler_kill(signum, frame):
    raise OSError("Killed!")


def execute(cmd_tokens):
    if cmd_tokens:
        # Extract command name and arguments from tokens
        cmd_name = cmd_tokens[0]
        cmd_args = cmd_tokens[1:]

        # If the command is a built-in command,
        # invoke its function with arguments
        if cmd_name in built_in_cmds:
            return built_in_cmds[cmd_name](cmd_args)
        # Wait for a kill signal
        signal.signal(signal.SIGINT, handler_kill)
        # Spawn a child process
        if platform.system() != "Windows":
            # Unix support
            sh = subprocess.Popen(cmd_tokens[0])
            # Parent process wait for child process
            sh.communicate()
        else:
            # Windows support
            command = ""
            for i in cmd_tokens:
                command = command + " " + i
            os.system(command)
    # Return status indicating to wait for next command in shell_loop
    return SHELL_STATUS_RUN


def shell_loop():
    status = SHELL_STATUS_RUN

    while status == SHELL_STATUS_RUN:
        # Display a command prompt
        if platform.system() != "Windows":
            if os.getcwd() == os.getenv('HOME'):
                dir = "~"
            else:
                dir = os.getcwd().split('/')[-1]
            if os.geteuid() != 0:
                sys.stdout.write(
                    '[' + getpass.getuser() + '@' +
                    socket.gethostname().split('.')[0] +
                    ' ' + dir + ']$ ')
            else:
                sys.stdout.write(
                    '[root@' + socket.gethostname().split('.')[0] +
                    ' ' + dir + ']# ')
        else:
            # Windows support
            sys.stdout.write(os.getcwd() + "> ")
        sys.stdout.flush()

        # Do not receive Ctrl signal
        if platform.system() != "Windows":
            signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        try:
            # Read command input
            cmd = sys.stdin.readline()
        except KeyboardInterrupt:
            _, err, _ = sys.exc_info()
            print(err)

        try:
            # Tokenize the command input
            cmd_tokens = tokenize(cmd)
        except:
            print("Error when receiving the command")
        # Fix a bug with inputing nothing
        try:
            # Execute the command and retrieve new status
            status = execute(cmd_tokens)
        except OSError:
            _, err, _ = sys.exc_info()
            print(err)


# Register a built-in function to built-in command hash map
def register_command(name, func):
    built_in_cmds[name] = func


# Register all built-in commands here
def init():
    register_command("cd", cd)
    register_command("exit", exit)
    register_command("getenv", getenv)
    register_command("export", export)


def main():
    # Init shell before starting the main loop
    init()
    shell_loop()

if __name__ == "__main__":
    main()
