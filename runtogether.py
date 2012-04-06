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


def killtree(pid, signal):
	"""
	Recursively kills all children of the process with given pid.
	Source: http://stackoverflow.com/a/3211182/263061
	"""
	script = """
		killTree() {
		    local _pid=$1
		    local _sig=${2-TERM}
		    for _child in $(ps -o pid --no-headers --ppid ${_pid}); do
		        killTree ${_child} ${_sig}
		    done
		    kill -${_sig} ${_pid}
		}

		killTree %d %s
	""" % (pid, signal)

	subprocess.call(['bash', '-c', script])


def runtogether(commands, kill_timeout=3, shutdown_callback=None, poll_interval=0.2):
	"""
	Runs the given commands in subprocesses.
	Terminates all of them as soon as one of them terminates.
	The exit code is set to the exit code of the first terminated process.
	Also terminates them on Ctrl-C (with return code 130).
	"""

	procs = []

	def shutdown(exit_code):
		print("Asking all child processes to terminate...")

		for proc in procs:
			if proc.poll() is None:
				killtree(proc.pid, "TERM")
		if any( p.poll() is None for p in procs ):
			time.sleep(kill_timeout)
			print("Killing remaining child processes...")
			for proc in procs:
				if proc.poll() is None:
					killtree(proc.pid, "KILL")
		print("done.")
		if shutdown_callback is not None:
			shutdown_callback()
		sys.exit(exit_code)

	signal.signal(signal.SIGTERM, lambda signum, stack_frame: shutdown(130))
	signal.signal(signal.SIGINT, lambda signum, stack_frame: shutdown(130))

	# Spawn subprocesses
	for command in commands:
		# Try to prevent children from capturing Ctrl-C with os.setsid
		try:
			proc = subprocess.Popen(shlex.split(command), preexec_fn=os.setsid)
		except:
			import traceback
			# Don't hide the exception
			traceback.print_exc()
			shutdown(1)
		print("Launched child with pid %d: %s" % (proc.pid, command))
		procs.append(proc)

	while True:
		for proc in procs:
			ret = proc.poll()
			if ret is None:
				continue
			else:
				print("Child with pid %d terminated with exit code %d!" % (proc.pid, ret))
				shutdown(ret)
		time.sleep(poll_interval)
