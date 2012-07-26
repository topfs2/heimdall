import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

class ChangeVideoToMovie(tasks.SubjectTask):
	demand = [
		demands.requiredClass("item.video")
	]

	supply = [
		supplies.replace(rdf.Class, "item.video.Movie"),
	]

	def run(self):
		self.subject.Class = "item.video.Movie"

module = [ ChangeVideoToMovie ]
