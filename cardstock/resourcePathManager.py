# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
            if self.pathMap and hasattr(sys, "_MEIPASS"):
                # we are running in a standalone app bundle
                base_dir = sys._MEIPASS
                if not os.path.exists(os.path.join(base_dir, path)):
                    base_dir = os.path.join(os.path.dirname(sys.executable), 'Resources')
            else:
                base_dir = os.path.dirname(self.stackManager.filename)
        else:
            base_dir = os.getcwd()

        absPath = os.path.join(base_dir, path)
        self.pathCache[path] = absPath
        return absPath


