from collections import deque
from collections import namedtuple
import threading

class Runnable(object):
	def run(self, *args, **kwargs):
		pass

class Callback(object):
	def onDone(self, runnable, error, result):
		pass

class ThreadPool(object):
	def append(self, runnable, callback, *args, **kwargs):
		pass

WorkItem = namedtuple("WorkItem", [ "runnable", "callback", "args", "kwargs" ])

def safe_run(runnable, args, kwargs):
	if callable(runnable):
		return runnable(*args, **kwargs)
	else:
		return runnable.run(*args, **kwargs)

def safe_callback(callback, runnable, error, result):
	if callable(callback):
		callback(runnable, error, result)
	else:
		callback.onDone(runnable, error, result)

class MainloopThreadPool(object):
	def __init__(self):
		self.condition = threading.Condition()
		self.queue = deque()

	def append(self, runnable, callback, *args, **kwargs):
		self.queue.append(WorkItem(runnable, callback, args, kwargs))

	def join(self):
		while len(self.queue) > 0:
			wi = self.queue.popleft()
			error = None
			result = None
			try:
				result = safe_run(wi.runnable, wi.args, wi.kwargs)
			except Exception as e:
				error = e
			finally:
				safe_callback(wi.callback, wi.runnable, error, result)