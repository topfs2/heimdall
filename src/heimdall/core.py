import tasks
from taskqueue import TaskQueue
import triggers
import utils

import json
import types
import threading
from collections import defaultdict

def isolate_if_single(d):
	if d == None or len(d) == 0:
		return None
	elif len(d) == 1:
		return d[0]
	else:
		return d

class Subject(object):
	def __init__(self, uri, subjectTasks, taskQueue):
		self.condition = threading.Condition()
		self.condition.acquire()

		self.uri = uri
		self.subject = defaultdict(list)

		self.availableTasks = [t for t in subjectTasks]
		self.taskQueue = taskQueue

		# Trigger subject creation tasks
		self._trigger(triggers.SubjectCreation)
		self.condition.release()

	def _trigger(self, classInfo):
		# Filter tasks of interest
		tasks = [t for t in self.availableTasks if isinstance(t.trigger, classInfo) and t.trigger.match(self)]

		for t in tasks:
			self.taskQueue.addTask(t(self), self)
			self.availableTasks.remove(t) # Once a task has been triggered it will be removed from available tasks

	def __getitem__(self, name):
		# No lock since pythons dict should be thread safe
		return isolate_if_single(self.subject.get(name, None))

	def emit(self, predicate, object):
		self.condition.acquire()
		if object != None:
			self.subject[predicate].append(object)

			# Trigger subject emit tasks
			self._trigger(triggers.SubjectEmit)
		self.condition.release()

	def replace(self, predicate, object, objectToReplace = None):
		raise NotImplementedError("Not finished")

	def dump(self):
		s = dict()
		for key, value in self.subject.items():
			value = isolate_if_single(value)
			if value:
				s[key] = value

		return s

	def onDone(self, task, error, result):
		self.condition.acquire()

		self.condition.release()

class Engine(object):
	def __init__(self, threadPool):
		self.registeredTasks = list()
		self.threadPool = threadPool

	def registerModule(self, module):
		self.registeredTasks.extend([t for t in module if issubclass(t, tasks.SubjectTask)])

	def get(self, uri):
		subject = Subject(uri, self.registeredTasks, utils.SubjectTaskQueue(self.threadPool))
		return subject
