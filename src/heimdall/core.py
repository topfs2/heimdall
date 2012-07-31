import tasks
import triggers
import taskqueues
import demands, supplies

import json
import types
import threading
from collections import defaultdict
from itertools import permutations
from itertools import combinations

import logging
log = logging.getLogger("heimdall.core")

def isolate_if_single(d):
	if d == None or len(d) == 0:
		return None
	elif len(d) == 1:
		return d[0]
	else:
		return d

def find_doable_tasks(subject, given_tasks):
	return [t for t in given_tasks if all([d.matches(subject) for d in t.demand])]

def find_impossible_tasks(subject, given_tasks):
	return [t for t in given_tasks if any([d.matches(subject) == demands.match.NEVER for d in t.demand])]

def purge_impossible_tasks(subject, given_tasks):
	impossible_tasks = find_impossible_tasks(subject, given_tasks)
	return [t for t in given_tasks if t not in impossible_tasks]

def conflicts(this, that):
	for ss in this.supply:
		for os in that.supply:
			if ss.conflict(os):
				return True

	return False

def find_conflicting_tasks(given_tasks):
	conflicting_tasks = list()

	for c in permutations(given_tasks, 2):
		if c[0] != c[1] and conflicts(c[0], c[1]):
			conflicting_tasks.append(c[0])

	return set(conflicting_tasks)

def purge_conflicting_tasks(tasks):
	conflicting_tasks = find_conflicting_tasks(tasks)
	return [t for t in tasks if t not in conflicting_tasks]

class Subject(object):
	def __init__(self, uri, subjectTasks, taskQueue, callback):
		self.condition = threading.Condition()

		self.uri = uri
		self.Class = ""
		self.subject = defaultdict(list)
		self.callback = callback

		self.runningTasks = list()
		self.availableTasks = [t for t in subjectTasks]

		self.taskQueue = taskQueue

		self.task_path = list() # For debugging purposes
		self._scheduleNonConflictingTasks()

	def __getitem__(self, name):
		# No lock since pythons dict should be thread safe
		return isolate_if_single(self.subject.get(name, None))

	def emit(self, predicate, object):
		self.condition.acquire()

		if object != None and object != "":
			self.subject[predicate].append(object)

		self.condition.release()

	def replace(self, predicate, object):
		self.condition.acquire()
		if object != None:
			if predicate in self.subject:
				del self.subject[predicate]

			self.subject[predicate].append(object)
		self.condition.release()

	def dump(self):
		s = dict()
		for key, value in self.subject.items():
			value = isolate_if_single(value)
			if value:
				s[key] = value

		return s

	def __repr__(self):
		s = {
			"Subject": {
				"id": self.uri,
				"Class": self.Class,
				"metadata": self.dump()
			}
		}

		return json.dumps(s, sort_keys=True, indent=4)

	def _scheduleNonConflictingTasks(self):
		possible_tasks = purge_impossible_tasks(self, self.availableTasks)
		doable_tasks = find_doable_tasks(self, possible_tasks)
		doable_tasks = purge_conflicting_tasks(doable_tasks)

		if len(doable_tasks) > 0:
			for t in doable_tasks:
				createdTask = t(self)
				self.runningTasks.append(createdTask)
				self.taskQueue.addTask(createdTask, self)

			self.task_path.append(doable_tasks)
		else:
			log.debug("Final scheduling order became", self.task_path)
			self.callback(None, self)

		self.availableTasks = [t for t in possible_tasks if t not in doable_tasks]

	def onDone(self, task, error, result):
		if error:
			self.callback(error, None)
		else:
			self.condition.acquire()

			if task in self.runningTasks:
				self.runningTasks.remove(task)

			if len(self.runningTasks) == 0:
				self._scheduleNonConflictingTasks()

			self.condition.release()

class Engine(object):
	def __init__(self, threadPool):
		self.registeredTasks = list()
		self.threadPool = threadPool

	def registerModule(self, module):
		self.registeredTasks.extend([t for t in module if issubclass(t, tasks.SubjectTask)])

	def get(self, uri, callback):
		subject = Subject(uri, self.registeredTasks, taskqueues.SubjectTaskQueue(self.threadPool), callback)
		return subject
