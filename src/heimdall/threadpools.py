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
		self.run = True

	def append(self, runnable, callback, *args, **kwargs):
		self.condition.acquire()
		self.queue.append(WorkItem(runnable, callback, args, kwargs))
		self.condition.notifyAll()
		self.condition.release()

	def quit(self):
		self.condition.acquire()
		self.run = False
		self.condition.notifyAll()
		self.condition.release()

	def join(self):
		self.condition.acquire()
		while self.run:
			if len(self.queue) > 0:
				wi = self.queue.popleft()
				error = None
				result = None
				try:
					result = safe_run(wi.runnable, wi.args, wi.kwargs)
				except Exception as e:
					error = e
				finally:
					safe_callback(wi.callback, wi.runnable, error, result)
			else:
				try:
					self.condition.wait()
				except Exception as e:
					raise e
		self.condition.release()

class ThreadedWorker(threading .Thread):
	def __init__(self, owner):
		super(ThreadedWorker, self).__init__()
		self.owner = owner
		self.start()

	def run(self):
		wi = self.owner.getNextWorkItem()

		while wi:
			error = None
			result = None
			try:
				result = safe_run(wi.runnable, wi.args, wi.kwargs)
			except Exception as e:
				error = e
			finally:
				safe_callback(wi.callback, wi.runnable, error, result)

			wi = self.owner.getNextWorkItem()

		self.owner.onDone(self)

class ThreadedThreadPool(object):
	def __init__(self, numberWorkers):
		self.condition = threading.Condition()
		self.queue = deque()
		self.acceptNewTasks = True
		self.numberWorkers = numberWorkers
		self.workers = list()

	def append(self, runnable, callback, *args, **kwargs):
		self.condition.acquire()
		if self.acceptNewTasks:
			self.queue.append(WorkItem(runnable, callback, args, kwargs))
			if len(self.workers) < self.numberWorkers:
				self.workers.append(ThreadedWorker(self))
			self.condition.notifyAll()
		self.condition.release()

	def getNextWorkItem(self):
		self.condition.acquire()
		wi = None
		if len(self.queue) > 0:
			wi = self.queue.popleft()
		self.condition.notifyAll()
		self.condition.release()
		return wi

	def onDone(self, worker):
		self.condition.acquire()
		self.workers.remove(worker)
		self.condition.notifyAll()
		self.condition.release()

	def join(self):
		self.condition.acquire()
		while len(self.workers) > 0 and len(self.queue) > 0:
			self.condition.wait()
		self.condition.release()

	def quit(self):
		self.condition.acquire()
		self.queue = deque()
		self.acceptNewTasks = False
		self.condition.notifyAll()
		self.condition.release()
