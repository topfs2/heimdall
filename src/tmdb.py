import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import triggers
from heimdall.predicates import *

import json
from urllib import unquote_plus, quote_plus

tmdb_base = "http://api.themoviedb.org/3"

class MoviePredicateObject(tasks.SubjectTask):
	trigger = triggers.SubjectCreation("http://api.themoviedb.org/3/movie/")

	def require(self):
		return [ 
			resources.SimpleResource(tmdb_base + "/configuration?api_key=57983e31fb435df4df77afb854740ea9"),
			resources.SimpleResource(self.subject.uri + "?api_key=57983e31fb435df4df77afb854740ea9")
		]

	def run(self, configuration, resource):
		c = json.loads(configuration)
		movie = json.loads(resource)

		self.subject.emit(dc.title, movie["original_title"])
		self.subject.emit(dc.description, movie["overview"])
		self.subject.emit(owl.sameAs, "http://www.imdb.com/title/" + movie["imdb_id"])
		self.subject.emit(foaf.homepage, movie["homepage"])

		images = c["images"]
		image_base = images["base_url"]

		for size in images["poster_sizes"]:
			self.subject.emit(foaf.thumbnail, image_base + size + movie["poster_path"])

		for size in images["backdrop_sizes"]:
			self.subject.emit("fanart", image_base + size + movie["poster_path"])

class SearchMovieCollector(tasks.SubjectTask):
	trigger = triggers.SubjectEmit(rdf.Class, video.Movie)

	def require(self):
		title = self.subject[dc.title]
		path = "http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + quote_plus(title)

		return resources.SimpleResource(path)

	def run(self, resource):
		result = json.loads(resource)

		ID = result["results"][0]["id"]
		tm = "http://api.themoviedb.org/3/movie/" + str(ID)

		self.subject.emit(owl.sameAs, tm)

module = [ SearchMovieCollector, MoviePredicateObject ]
