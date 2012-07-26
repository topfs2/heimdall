import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import mutagen

class ExtractTags(tasks.SubjectTask):
	demand = [
		demands.requiredClass("item.audio")
	]

	supply = [
		supplies.replace(dc.title),
		supplies.emit("album"),
		supplies.emit("artist")
	]

	def run(self):
		f = mutagen.File(self.subject.uri[7:], easy=True)
		self.subject.emit("album", f["album"][0])
		self.subject.emit("artist", f["artist"][0])
		self.subject.replace(dc.title, f["title"][0])

module = [ ExtractTags ]
