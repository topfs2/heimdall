import re
import types

class Trigger(object):
	pass

class SubjectCreation(Trigger):
	def __init__(self, uri):
		self.uri = uri

	def match(self, subject):
		return re.match(self.uri, subject.uri)

class SubjectEmit(Trigger):
	def __init__(self, predicate, object):
		self.predicate = predicate
		self.object = object

	def match(self, subject):
		objects = subject[self.predicate]
		if type(objects) == types.ListType:
			return self.object in objects
		else:
			return objects == self.object
