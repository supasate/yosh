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
        # Find the `=` sign
        equal_pos = el.find('=')
        if (equal_pos > 0 and
                el[equal_pos - 1] != '=' and
                el[equal_pos + 1] != '='):
            token.append(str(token[i]))
            token[i] = "export"
            break
        # Find the dollar sign
        if el.startswith('$'):
            if el.find('/') != -1:
                strf = str(token[i][1:el.find('/')])
                token[i] = str(os.getenv(token[i][1:el.find('/')])) + str(
                    token[i][el.find('/'):len(token[i])])
            # Windows Support
            elif el.find('\\') != -1:
                strf = str(token[i][1:el.find('\\')])
                token[i] = str(os.getenv(token[i][1:el.find('\\')])) + \
                    str(token[i][el.find('\\'):len(token[i])])
            else:
                token[i] = str(os.getenv(token[i][1:]))
            break
        # `*` sign does not support Windows
        if platform.system() == "Windows":
            break
        # Find the `*` sign
        if el.find("*") != -1:
            if el.find("/") == -1:
                for files in os.listdir(os.getcwd()):
                    if files.find(el.strip("./*")) != -1:
                        token[i] = os.getcwd() + "/" + files
                        break
            elif el.find("./") != -1:
                for files in os.listdir(os.getcwd()):
                    if files.find(el.strip("./*")) != -1:
                        token[i] = os.getcwd() + "/" + files
                        break
            else:
                found = False
                for files in os.listdir(token[i][0:el.rfind('/')]):
                    if found:
                        break
                    if files.find(el.strip(
                                  token[i][0:el.rfind('/')] + "*")) != -1:
                        token[i] = "/" + el.strip(token[i][
                            el.rfind('/') + 1:len(el)] + "*") + "/" + files
                        found = True
                        break
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
            found = False
            # Std including "stdin" and "stdout"
            std = False
            waitpid = False
            # Auto find the command
            for path in os.getenv("PATH").split(":"):
                if os.path.exists(path + "/" + cmd_name):
                    for a, el in enumerate(cmd_tokens):
                        # Find the '>'
                        if el == ">":
                            with open(cmd_tokens[a + 1], "a") as f:
                                f.flush()
                                # Fix the cmd_tokens
                                p = subprocess.Popen(cmd_tokens[0:a], stdout=f)
                                std = True
                                found = True
                                break
                        # Find the '<'
                        elif el == "<":
                            with open(cmd_tokens[a + 1], "r+") as g:
                                p = subprocess.Popen(cmd_tokens[0:a], stdin=g)
                                std = True
                                found = True
                                break
                        # Find the '&' sign,and run in the background
                        elif el == "&":
                            p = subprocess.Popen(cmd_tokens,
                                                 stdout=subprocess.PIPE)
                            waitpid = True
                            break
                    if not std:
                        if not waitpid:
                            p = subprocess.Popen(cmd_tokens)
                            # Parent process read data from child process
                            # and wait for child process to exit
                            p.communicate()
                        found = True
                        break
            if not found:
                for i in os.getenv("PATH").split(":"):
                    for files in os.listdir(i):
                        if files.find(cmd_tokens[0]) != -1:
                            print "Do you mean: " + files
                            found = False
                            break
            if not found:
                print "File Not Found"

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
            with open(os.getenv('HOME') + "/.yosh_history", "a") as his_file:
                his_file.write(cmd)
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
    register_command("history", history)


def main():
    # Init shell before starting the main loop
    init()
    shell_loop()

if __name__ == "__main__":
    main()
