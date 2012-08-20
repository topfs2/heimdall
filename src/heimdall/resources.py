import tasks
try:
    import requests
    def vfs_read(uri):
        return requests.get(uri).content
except:
    import urllib
    def vfs_read(uri):
        return urllib.urlopen(uri).read()

class Resource(tasks.Task):
    """
    Raw resource task, when acquired as requirement it may be used to access the
    resource in its rawest form. Will behave much like a standard file object.
    """
    def __init__(self, uri):
        self.uri = uri

    def run(self):
        return self

    def read(self):
        return vfs_read(self.uri)

class SimpleResource(tasks.Task):
    """
    Simpler resource access, when acquired as requirement it will give the entire
    resource as result. This is useful when a resource is needed in its entirety
    to process. Examples of can be text files such as xml, json etc. The resource
    is not parsed and its binary form is read.
    """
    def __init__(self, uri):
        self.uri = uri

    def require(self):
        return Resource(self.uri)

    def run(self, resource):
        return resource.read()
