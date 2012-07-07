import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import triggers
from heimdall.predicates import *

import json
from urllib import unquote_plus, quote_plus
from urlparse import urlsplit

mime_types = {
	".mkv": "video/x-matroska",
	".avi": "video/avi"
}

mime_type_to_class = {
	"video/x-matroska": video.Recording
}

class ItemPredicateObject(tasks.SubjectTask):
	trigger = triggers.SubjectCreation("file://")

	def run(self):
		path = urlsplit(self.subject.uri).path
		ext = path[path.rindex("."):].lower()
		mime_type = mime_types.get(ext, None)

		title = path[path.rindex("/") + 1:path.rindex(".")]
		title = title.replace(".", " ")

		self.subject.emit(dc.title, title)
		self.subject.emit(dc.format, mime_type)

		self.subject.emit(rdf.Class, mime_type_to_class.get(mime_type, media.Recording))

class ChangeVideoToMovie(tasks.SubjectTask):
	trigger = triggers.SubjectEmit(rdf.Class, video.Recording)

	def run(self):
		self.subject.emit(rdf.Class, video.Movie)

module = [ ItemPredicateObject, ChangeVideoToMovie ]
