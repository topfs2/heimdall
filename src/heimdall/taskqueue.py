import tasks

import threading
import types
from collections import defaultdict
import sys

# Placeholder for when requirements are needed but not available
class NotFilled(object):
	pass

class WorkItem(object):
	def __init__(self, task, requirements):
		self.task = task
		self.requirements = requirements
		self.parameters = [ NotFilled for r in requirements ] if requirements != None else [ ]

	def okToGo(self):
		return not any([x is NotFilled for x in self.parameters])

class Worker(threading.Thread):
	def __init__(self, pool):
		super(Worker, self).__init__()
		self.pool = pool
		self.start()

	def run(self):
		wi = self.pool.getNextTask()

		while wi:
			result = None
			try:
				result = wi.task.run(*wi.parameters)
			except Exception as e:
				print wi.task, "Error running task. Exception:", type(e), e
			finally:
				self.pool.onDone(wi.task, result)

			wi = self.pool.getNextTask()

def _buildOrderedListOfRequirements(lst, job):
	requirements = job.require()

	if requirements != None:
		requirements = requirements if type(requirements) == types.ListType else [ requirements ]
		for r in requirements:
			_buildOrderedListOfRequirements(lst, r)

	lst.append(WorkItem(job, requirements))

class TaskQueue(object):
	def __init__(self, threads):
		self.condition = threading.Condition()
		self.acceptNewTasks = True
		self.queues = defaultdict(list)
		self.callbacks = dict()
		self.runningTasks = dict()

		self.condition.acquire()
		self.workers = [ Worker(self) for _ in range(threads)]
		self.condition.release()

	def __del__(self):
		print "Deleting threadpool"
		self.shutdown()

	# Will block until task has been added to the queue, will normally be quick
	def addTask(self, task, queueID, callback = None):
		self.condition.acquire()
		try:
			lst = list()
			_buildOrderedListOfRequirements(lst, task)

			# Now when all requirements are successfully created, add them to our queue
			self.queues[queueID].extend(lst)
			self.callbacks[queueID] = callback

			self.condition.notifyAll()
		except Exception as e:
			print task, "Error adding task. Exception:", type(e), e

		self.condition.release()

	# Will block until a task is available, when it returns null there is no more
	# work to be done, i.e. close the worker
	def getNextTask(self):
		self.condition.acquire()
		nextToGo = None

		def findRunnableTask():
			for queue in self.queues.values():
				for wi in queue:
					if wi.okToGo():
						queue.remove(wi)
						self.runningTasks[wi.task] = wi
						return wi

			return None

		while nextToGo == None and (self.acceptNewTasks or len(self.queues)):
			nextToGo = findRunnableTask()

			if nextToGo == None:
				self.condition.wait()

		self.condition.release()
		return nextToGo

	def onDone(self, task, result):
		self.condition.acquire()

		for key, queue in self.queues.items():
			for wi in queue:
				if wi.requirements != None and task in wi.requirements:
					wi.parameters[wi.requirements.index(task)] = result

			if len(queue) == 0:
				if key in self.callbacks and self.callbacks[key]:
					self.callbacks[key](key)

				del self.queues[key]

		del self.runningTasks[task]

		self.condition.notifyAll()
		self.condition.release()

	def wait(self, queueID = None):
		self.condition.acquire()

		if queueID == None:
			while len(self.queues) > 0 or len(self.runningTasks) > 0:
				self.condition.wait()
		else:
			while queueID in self.queues or len(self.runningTasks) > 0:
				self.condition.wait()

		self.condition.release()

	def shutdown(self, wait=True, finishQueue=True):
		self.condition.acquire()

		print "Shutting down"

		self.acceptNewTasks = False

		if finishQueue == False:
			self.queues = dict()

		self.condition.notifyAll()
		self.condition.release()

		if wait:
			for w in self.workers:
				w.join()

		print "Shut down"
