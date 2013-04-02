import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

from pymediainfo import MediaInfo

from urlparse import urlparse

class ExtractStreamDetails(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier, "^file://"),
        demands.requiredClass("item", True)
    ]

    supply = [
        supplies.replace(rdf.Class, "item.audio"),
        supplies.replace(rdf.Class, "item.video"),
        supplies.emit("video_stream"),
        supplies.emit("audio_stream")
    ]

    def run(self):
        uri = urlparse(self.subject[dc.identifier]).path

        if uri:
            media_info = MediaInfo.parse(uri)

            video_streams = list()
            audio_streams = list()

            for track in media_info.tracks:
                if track.track_type == 'General' and track.duration:
                    self.subject.emit("duration", track.duration / 1000.0)
                elif track.track_type == 'Video':
                    v = dict()

                    if track.frame_rate:
                        v["framerate"] = float(track.frame_rate)
                    if track.codec:
                        v["codec"] = track.codec
                    if track.height:
                        v["height"] = int(track.height)
                    if track.width:
                        v["width"] = int(track.width)

                    video_streams.append(v)
                elif track.track_type == "Audio":
                    a = dict()

                    if track.sampling_rate:
                        a["samplerate"] = int(track.sampling_rate)
                    if track.codec:
                        a["codec"] = track.codec
                    if track.channel_s:
                        a["channels"] = int(track.channel_s)

                    audio_streams.append(a)

            for v in video_streams:
                self.subject.emit("video_stream", v)

            for a in audio_streams:
                self.subject.emit("audio_stream", a)

            if len(video_streams) > 0:
                self.subject.extendClass("item.video")
            elif len(audio_streams) > 0:
                self.subject.extendClass("item.audio")

module = [ ExtractStreamDetails ]
