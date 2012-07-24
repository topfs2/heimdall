#!/usr/bin/python

from heimdall.core import Engine
from heimdall.predicates import *
from heimdall.utils import MainloopThreadPool

import tmdb
import item
import json

import debug

import time

def main():
	pool = MainloopThreadPool()
	engine = Engine(pool)
	engine.registerModule(tmdb.module)
	engine.registerModule(item.module)

	subjects = dict()

	uri = "file:///home/SomeUser/movies/Horrible Bosses.mkv" # A file which doesn't exist, just used for testing
	s = engine.get(uri)

	pool.join()

	print json.dumps(s.dump(), sort_keys=True, indent=4)

if __name__ == "__main__":
    main()
