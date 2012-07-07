import tasks
from taskqueue import TaskQueue
from subject import Subject

class Engine(object):
	def __init__(self):
		self.registeredTasks = list()
		self.taskQueue = TaskQueue(10)

	def registerModule(self, module):
		self.registeredTasks.extend([t for t in module if issubclass(t, tasks.SubjectTask)])

	def get(self, uri):
		subject = Subject(uri, self.registeredTasks, self.taskQueue)
		return subject

	def wait(self, uri = None):
		self.taskQueue.wait(uri)

	def shutdown(self):
		self.taskQueue.shutdown()
