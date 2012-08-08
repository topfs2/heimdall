import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

from pymediainfo import MediaInfo

import json

class ExtractStreamDetails(tasks.SubjectTask):
	demand = [
		demands.requiredClass("item", True)
	]

	supply = [
		supplies.replace(rdf.Class, "item.audio"),
		supplies.replace(rdf.Class, "item.video"),
		supplies.emit("video_stream"),
		supplies.emit("audio_stream")
	]

	def run(self):
		uri = self.subject[dc.identifier]
		if uri[:7] == "file://":
			uri = uri[7:]
		elif uri[0] != "/":
			uri = None

		mime_type = self.subject[dc.format]

		if uri:
			media_info = MediaInfo.parse(uri)

			video_streams = list()
			audio_streams = list()

			for track in media_info.tracks:
#				print json.dumps(track.to_data(), indent=4, sort_keys=True)
#				print ""
				if track.track_type == 'Video':
					v = {
						"framerate": track.frame_rate,
						"duration": track.duration,
						"codec": track.codec,
						"channels": track.channel_s,
						"height": track.height,
						"width": track.width
					}

					video_streams.append(v)
				elif track.track_type == "Audio":
					a = {
						"duration": track.duration,
						"codec": track.codec,
						"channels": track.channel_s,
						"sample_rate": track.sampling_rate
					}
					audio_streams.append(a)

			for v in video_streams:
				self.subject.emit("video_stream", v)

			for a in audio_streams:
				self.subject.emit("audio_stream", a)

			if len(video_streams) > 0:
				self.subject.Class = "item.video"
			elif len(audio_streams) > 0:
				self.subject.Class = "item.audio"

module = [ ExtractStreamDetails ]
