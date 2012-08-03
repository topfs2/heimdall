class deferedrun(object):
	def __init__(self, runnable, requirements):
		self.runnable = runnable
		self.requirements = requirements

class Task(object):
	def preFlight(self):
		return deferedrun(self.run, self.require())

	# Return required tasks to run this task
	# All tasks needed should be created, i.e. return objects not classes
	# The data returned by an required task will be piped to the run method in order of require
	def require(self):
		pass

	# This method is called when all requirements are fulfilled in the requires return.
	# The function will be called with an unpacked list of the requirements in the same order as
	# the require function returned its dependencies. *require is a placeholder for this.
	# The task may return anything which is meant to be sent to a triggering task
	def run(self, *require):
		raise NotImplementedError("A Task must implement the run method")

# Subject Tasks are run "on" a subject, and tied to this subject.
# The subject will through the trigger member add this task to the task queue
# automatically, making it possible for a SubjectTask to specify when it should run but
# leaving control of actual launch to the subject and task queue.
class SubjectTask(Task):
	trigger = None

	demand = None
	supply = None

	def __init__(self, subject):
		self.subject = subject
