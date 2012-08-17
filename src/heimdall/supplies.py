import types
import re

class supply(object):
    pass

class predicateObjectSupply(supply):
    def __init__(self, predicate, object = None):
        self.predicate = predicate
        self.object = object

# TODO This should be in task rather
#        if isinstance(self.predicate, types.ListType) or isinstance(self.predicate, types.TupleType):
#            self.predicate = self.predicate[0]
#            self.object = self.predicate[1]

        if not isinstance(self.predicate, types.StringTypes):
            raise ValueError("Predicate must be string type")

        if not (isinstance(self.object, types.StringTypes) or self.object == None):
            raise ValueError("Object must be string type or None")

    def matches(self, demand):
        return hasattr(demand, "predicate") and self.predicate == demand.predicate

    def conflict(self, supply):
        return False

    def __str__(self):
        return "{0}({1}={2})".format(self.__class__.__name__, self.predicate, str(self.object))

# The task might supply emit predicate(s) (and object) when run
class emit(predicateObjectSupply):
    pass

# The task might when run replace the predicate (and object(s))
class replace(predicateObjectSupply):
    def conflict(self, supply):
        return isinstance(supply, emit) and supply.predicate == self.predicate

# Will upgrade the predicate object
class upgrade(replace):
    pass

class ugpradeClass(supply):
    def __init__(self, Class):
        self.Class = Class

    def __str__(self):
        return "ugpradeClass(rdf:Class={1})".format(self.Class)
