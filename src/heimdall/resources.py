import tasks
import requests

class Resource(tasks.Task):
	def __init__(self, uri):
		self.uri = uri

	def run(self):
		return self

	def read(self):
		response = requests.get(self.uri)
		return response.content


class SimpleResource(tasks.Task):
	def __init__(self, uri):
		self.uri = uri

	def require(self):
		return Resource(self.uri)

	def run(self, resource):
		return resource.read()
