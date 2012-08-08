import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

class GuessVideoOrEpisode(tasks.SubjectTask):
	demand = [
		demands.requiredClass("item.video"),
		demands.required("video_stream")
	]

	supply = [
		supplies.replace(rdf.Class, "item.video.Movie"),
		supplies.replace(rdf.Class, "item.video.Episode"),
	]

	def run(self):
		duration = self.subject["video_stream"]["duration"]

		if duration > 3600: # if longer than an hour, just guess movie
			self.subject.Class = "item.video.Movie"
		else:
			self.subject.Class = "item.video.Episode"

module = [ GuessVideoOrEpisode ]
