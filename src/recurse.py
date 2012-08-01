#!/usr/bin/python
# -*- coding: utf-8 -*-

from heimdall.core import Engine
from heimdall.predicates import *
from heimdall.threadpools import *

import themoviedb
import theaudiodb
import item
import video_item
import audio_item
import json

import debug

import time
from urlparse import urlparse
from urlparse import urlsplit, urlunsplit
from urllib import quote_plus, unquote_plus
import sys
import os

def main(folder):
	print "Running heimdall on folder", folder
	pool = MainloopThreadPool()
	engine = Engine(pool)
	engine.registerModule(themoviedb.module)
	engine.registerModule(theaudiodb.module)
	engine.registerModule(item.module)
	engine.registerModule(video_item.module)
	engine.registerModule(audio_item.module)

	subjects = list()

	fileList = []
	for root, subFolders, files in os.walk(folder):
		for f in files:
		    fileList.append(u"file://{0}/{1}".format(root,f))

	print "Files to process", len(fileList)

	fileList = fileList[:]

	nbrBeforeQuit = len(fileList)

	def c(error, subject):
		if error:
			raise error

		print subject
		subjects.append(subject)

		if len(subjects) >= nbrBeforeQuit:
			pool.quit()

	for f in fileList:
		engine.get(f, c)

	try:
		pool.join()
	except KeyboardInterrupt:
		pool.quit()

	print "done"

if __name__ == "__main__":
    main(sys.argv[1])
