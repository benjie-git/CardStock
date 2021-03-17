import os
import sys

class ResourcePathManager(object):
    """
    This class is in charge of converting relative paths to absolute, but also keeping track of the full set of
    resources (images and sounds) used by a stack, so they can all be included when exporting a standalone app.
    """
    def __init__(self, stackManager):
        super().__init__()
        self.stackManager = stackManager
        self.pathCache = {}
        self.pathMap = {}

    def Reset(self):
        self.pathCache = {}

    def SetPathMap(self, pathMap):
        self.pathMap = pathMap

    def GetRequestedPaths(self):
        return self.pathMap.keys()

    def GetAbsPath(self, path):
        if not path:
            return None

        if path in self.pathMap:
            path = self.pathMap[path]
        if path in self.pathCache:
            return self.pathCache[path]

        if self.stackManager.filename:
            if getattr(sys, 'frozen', False):
                # we are running in a bundle
                dir = sys._MEIPASS
            else:
                dir = os.path.dirname(self.stackManager.filename)
        else:
            dir = os.getcwd()

        absPath = os.path.join(dir, path)
        self.pathCache[path] = absPath
        return absPath


