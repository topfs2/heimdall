import heimdall
from heimdall import tasks
from heimdall import triggers

class RaiseErrorsAlways(tasks.SubjectTask):
	trigger = triggers.SubjectCreation("\w")

	def require(self):
		raise Exception("Exception during require")		

	def run(self):
		raise Exception("Exception during run")

class RaiseErrorsRun(tasks.SubjectTask):
	trigger = triggers.SubjectCreation("\w")

	def run(self):
		raise Exception("Exception during run")

class RaiseErrorAlwaysChain(tasks.Task):
	def require(self):
		raise Exception("Exception during require")		

	def run(self):
		raise Exception("Exception during run")

class RaiseErrorRunChain(tasks.Task):
	def run(self):
		raise Exception("Exception during run")

class RequireingAnRequireErrorTask(tasks.SubjectTask):
	trigger = triggers.SubjectCreation("\w")

	def require(self):
		return [ RaiseErrorAlwaysChain() ]

	def run(self):
		raise Exception("RequireingAnErrorTask during run")

class RequireingAnRunErrorTask(tasks.SubjectTask):
	trigger = triggers.SubjectCreation("\w")

	def require(self):
		return [ RaiseErrorRunChain() ]

	def run(self, errorous):
		# TODO This happens, SHOULD NOT
		raise Exception("RequireingAnRunErrorTask during run. Should NOT be run!")


module = [ RaiseErrorsAlways, RaiseErrorsRun, RequireingAnRequireErrorTask, RequireingAnRunErrorTask ]
