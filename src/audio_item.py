import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import mutagen
from urlparse import urlparse

class ExtractTags(tasks.SubjectTask):
	demand = [
		demands.requiredClass("item.audio")
	]

	supply = [
		supplies.replace(dc.title),
		supplies.emit(upnp.album),
		supplies.emit(upnp.artist),
		supplies.emit(upnp.originalTrackNumber),
	]

	def run(self):
		uri = urlparse(self.subject.uri)
		if uri.scheme == "file":
			f = mutagen.File(uri.path, easy=True)

			for album in f.get("album", []):
				self.subject.emit(upnp.album, album)

			for artist in f.get("artist", []):
				self.subject.emit(upnp.artist, artist)

			title = f.get("title", [])
			if len(title) > 0:
				self.subject.replace(dc.title, title[0])

			self.subject.Class = "item.audio.musicTrack"

module = [ ExtractTags ]
