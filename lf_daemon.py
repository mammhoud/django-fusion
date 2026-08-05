#!/usr/bin/env python3
"""Double-fork daemon runner — detaches a command from the calling process
group so it survives the harness's cleanup, logging to the file the command
redirects to. Usage: python3 lf_daemon.py "<shell command>"."""
import os
import sys

cmd = sys.argv[1] if len(sys.argv) > 1 else None
if not cmd:
    print("usage: lf_daemon.py '<command>'", file=sys.stderr)
    sys.exit(2)

# First fork
pid = os.fork()
if pid > 0:
    os._exit(0)

os.setsid()
os.umask(0)

# Second fork
pid = os.fork()
if pid > 0:
    os._exit(0)

# Redirect stdio to /dev/null (the command itself redirects to its log)
devnull = os.open(os.devnull, os.O_RDWR)
os.dup2(devnull, 0)
os.dup2(devnull, 1)
os.dup2(devnull, 2)

os.execvp("/bin/bash", ["/bin/bash", "-c", cmd])
