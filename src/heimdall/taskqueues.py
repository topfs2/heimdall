from collections import deque
from collections import namedtuple
import threading
import types

class NotFilled(object):
	pass

class ProxyTaskCallback(object):
	def __init__(self, threadPool, task, callback, requirements):
		self.threadPool = threadPool
		self.task = task
		self.callback = callback

		self.requirementMap = dict()
		self.requirements = list()

		for i in range(len(requirements)):
			r = requirements[i]
			self.requirementMap[r] = i
			self.requirements.append(NotFilled)

	def onDone(self, runnable, error, result):
		if error:
			self.callback(self.task, error, None)
		else:
			i = self.requirementMap[runnable]
			self.requirements[i] = result

			if all([r != NotFilled for r in self.requirements]):
				# Use the amount of requirements as priority, the more requirements a runnable have the more memory it has occupied so its a fair assesment on how quickly we want it to be done
				self.threadPool.append(self.task, self.callback, len(self.requirements), *self.requirements)

def buildProxy(threadPool, task, callback):
	requirements = task.require()

	if requirements:
		requirements = requirements if type(requirements) == types.ListType else [ requirements ]

		proxy = ProxyTaskCallback(threadPool, task, callback, requirements)
		for r in requirements:
			buildProxy(threadPool, r, proxy.onDone)
	else:
		threadPool.append(task, callback, 0)

class SubjectTaskQueue(object):
	def __init__(self, threadPool):
		self.threadPool = threadPool
		self.runningTasks = dict()
		self.condition = threading.Condition()

	# Will block until task has been added to the queue, will normally be quick
	def addTask(self, task, callback):
		with self.condition:
			try:
				buildProxy(self.threadPool, task, self.onDone)
				self.runningTasks[task] = callback
			except Exception as error:
				print task, "Error adding task. Exception:", type(error), error
				callback(task, error, None)

	def onDone(self, task, error, result):
		with self.condition:
			self.runningTasks[task](task, error, result)
			del self.runningTasks[task]
