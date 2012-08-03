import time
import threading
from collections import namedtuple

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

CacheItem = namedtuple("CacheItem", [ "value", "die" ])

class SimpleCache(object):
	def __init__(self):
		self.dataStore = dict()
		self.condition = threading.Condition()

	def get(self, key, default_factory, duration=60):
		with self.condition:
			now = time.time()

			# First lets purge any items which are old
			for key in self.dataStore.keys():
				if self.dataStore[key].die < now:
					del self.dataStore[key]

			# Fill cache with data if key not existant
			if key not in self.dataStore:
				self.dataStore[key] = CacheItem(default_factory(), now + duration)

			return self.dataStore[key].value
