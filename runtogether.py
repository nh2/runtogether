"""
A utility to start and terminate several background processes at once.
Tested with Python 2 and 3.
"""
from __future__ import print_function

import os
import shlex
import signal
import subprocess
import sys
import time
import atexit


def runtogether(commands, kill_timeout=3, shutdown_callback=None):
	"""
	Runs the given commands in subprocesses.
	Terminates all of them as soon as one of them terminates.
	The exit code is set to the exit code of the first terminated process.
	Also terminates them on Ctrl-C (with return code 130).
	"""

	procs = []

	def shutdown():
		print("Asking all child processes to terminate...")
		for proc in procs:
			if proc.poll() is None:
				proc.terminate()
		if any( p.poll() is None for p in procs ):
			time.sleep(kill_timeout)
			print("Killing remaining child processes...")
			for proc in procs:
				if proc.poll() is None:
					proc.kill()
					proc.wait()
		print("done.")
		if shutdown_callback is not None:
			shutdown_callback()

	atexit.register(shutdown)

	signal.signal(signal.SIGTERM, lambda signum, stack_frame: shutdown())
	signal.signal(signal.SIGINT, lambda signum, stack_frame: shutdown())

	# Spawn subprocesses
	for command in commands:
		# Try to prevent children from capturing Ctrl-C with os.setsid
		proc = subprocess.Popen(shlex.split(command), preexec_fn=os.setsid)
		procs.append(proc)

	while procs:
		for proc in procs:
			ret = proc.poll()
			if ret is None:
				continue
			else:
				procs.remove(proc)
				print("Child terminated with exit code %d!" % ret)
				sys.exit(ret)
		time.sleep(0.2)
