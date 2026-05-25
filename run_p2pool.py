#!/usr/bin/env python
import os
import sys

def _default_pidfile():
    runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
    if runtime_dir and os.path.isdir(runtime_dir) and os.access(runtime_dir, os.W_OK):
        return os.path.join(runtime_dir, 'p2pool.pid')
    state_dir = os.path.join(os.path.expanduser('~'), '.p2pool')
    os.makedirs(state_dir, mode=0o700, exist_ok=True)
    return os.path.join(state_dir, 'p2pool.pid')

pid = str(os.getpid())
pidfile = os.environ.get('P2POOL_PIDFILE', _default_pidfile())
pidfile_fd = None

try:
    pidfile_fd = os.open(pidfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    print("%s already exists, exiting" % pidfile)
    sys.exit()
with os.fdopen(pidfile_fd, 'w') as f:
    pidfile_fd = None
    f.write(pid) # write the pid to pidfile

try:
    # Real code
    from p2pool import main
    main.run()
finally:
    if pidfile_fd is not None:
        os.close(pidfile_fd)
    try:
        os.unlink(pidfile) # remove the pid lock file
    except FileNotFoundError:
        pass
