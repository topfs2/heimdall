import tasks

from collections import deque
from collections import namedtuple
import threading
import types

class NotFilled(object):
	pass

class TaskQueue(object):
	def __init__(self, threadPool):
		self.threadPool = threadPool

		self.condition = threading.Condition()
		self.runnableOwnerMap = dict()
		self.taskDataMap = dict()
		self.requirementOwnerMap = dict()

	def addTask(self, task, callback):
		with self.condition:
			taskData = {
				"task": task,
				"callback": callback,
				"requirementsMap": dict(),
				"requirements": list(),
				"runnable": None
			}

			self.taskDataMap[task] = taskData

			rr = task.preFlight()
			self._addRunnable(task, rr.runnable, rr.requirements)

	def _addRunnable(self, owner, runnable, requirements):
		with self.condition:
			self.runnableOwnerMap[runnable] = owner
			taskData = self.taskDataMap[owner]

			taskData["runnable"] = runnable
			taskData["requirementsMap"] = dict()
			taskData["requirements"] = list()

			if requirements:
				requirements = requirements if type(requirements) == types.ListType else [ requirements ]

				for r in requirements:
					taskData["requirementsMap"][r] = len(taskData["requirements"])
					taskData["requirements"].append(NotFilled)
					self.requirementOwnerMap[r] = owner
					self.addTask(r, self.onRequirementDone)
			else:
				self.threadPool.append(runnable, self.onRunnableDone, 0)

	def onRunnableDone(self, runnable, error, result):
		with self.condition:
			owner = self.runnableOwnerMap[runnable]
			taskData = self.taskDataMap[owner]

			if error:
				self.onTaskDone(taskData["task"], error, None)
			elif isinstance(result, tasks.deferedrun):
				self._addRunnable(self.runnableOwnerMap[runnable], result.runnable, result.requirements)
			else:
				self.onTaskDone(taskData["task"], None, result)

			del self.runnableOwnerMap[runnable]

	def onTaskDone(self, task, error, result):
		with self.condition:
			taskData = self.taskDataMap[task]
			taskData["callback"](task, error, result)

			del self.taskDataMap[task]

	def onRequirementDone(self, r, error, result):
		with self.condition:
			owner = self.requirementOwnerMap[r]
			taskData = self.taskDataMap[owner]

			if error:
				self.callback(taskData["task"], error, None)
			else:
				i = taskData["requirementsMap"][r]
				taskData["requirements"][i] = result

				requirements = taskData["requirements"]

				if all([req != NotFilled for req in requirements]):
					self.threadPool.append(taskData["runnable"], self.onRunnableDone, len(requirements), *requirements)

			del self.requirementOwnerMap[r]
