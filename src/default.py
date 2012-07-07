#!/usr/bin/python

import heimdall.engine
from heimdall.predicates import *
import tmdb
import item
import json

import debug

import time

def main():
	engine = heimdall.engine.Engine()
	try:
		engine.registerModule(tmdb.module)
		engine.registerModule(item.module)
		engine.registerModule(debug.module)

		subjects = dict()

		uri = "file:///home/SomeUser/movies/Horrible Bosses.mkv" # A file which doesn't exist, just used for testing
		s = engine.get(uri)

		engine.wait()

		print json.dumps(s.dump(), sort_keys=True, indent=4)

		try:
			next = engine.get(s[owl.sameAs])

			engine.wait()
			print json.dumps(next.dump(), sort_keys=True, indent=4)
		except:
			pass
	except Exception as e:
		print "Exception", e
	finally:
		engine.shutdown()

if __name__ == "__main__":
    main()
