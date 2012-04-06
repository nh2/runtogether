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


def runtogether(commands, kill_timeout=3, shutdown_callback=None):
	"""
	Runs the given commands in subprocesses.
	Terminates all of them as soon as one of them returns a non-0 exit code.
	Also terminates them on Ctrl-C.
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
		sys.exit(1)

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
			if ret != 0:
				print("Child terminated with exit code!")
				shutdown()
		time.sleep(0.2)
