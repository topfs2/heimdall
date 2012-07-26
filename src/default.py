#!/usr/bin/python

from heimdall.core import Engine
from heimdall.predicates import *
from heimdall.threadpools import MainloopThreadPool

import tmdb
import item
import video_item
import json

import debug

import time

def main():
	pool = MainloopThreadPool()
	engine = Engine(pool)
	engine.registerModule(tmdb.module)
	engine.registerModule(item.module)
	engine.registerModule(video_item.module)

	subjects = dict()

	uri = "file:///home/SomeUser/movies/Horrible Bosses.mkv" # A file which doesn't exist, just used for testing
	def c(s):
		print s

	s = engine.get(uri, c)

	pool.join()

#	print json.dumps(s.dump(), sort_keys=True, indent=4)

if __name__ == "__main__":
    main()
