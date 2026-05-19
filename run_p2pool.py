#!/usr/bin/env python
import os
import sys
pid = str(os.getpid())
pidfile = "/tmp/p2pool.pid"

if os.path.isfile(pidfile):
	print "%s already exists, exiting" % pidfile
	sys.exit()
file(pidfile, 'w').write(pid) # write the pid to pidfile

try:
	# Real code
	from p2pool import main
	main.run()
finally:
	os.unlink(pidfile) # remove the pid lock file
