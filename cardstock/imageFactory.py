# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx


class ImageFactory(object):
    """ Keep wxImages around and sorted by size, so we can avoid creating new ones every time we need to use one to build a region. """

    imgFactory = None

    @classmethod
    def shared(cls):
        if not cls.imgFactory:
            cls.imgFactory = ImageFactory()
        return cls.imgFactory

    def __init__(self):
        self.map = None
        self.ClearCache()

    def ClearCache(self):
        self.map = {}

    @staticmethod
    def NormalizeSize(w, h):
        (w, h) = (int(w), int(h))
        return (w+(63-((w-1)%64)), h+(63-((h-1)%64)))

    def RecycleImage(self, img):
        (w, h) = self.NormalizeSize(*img.GetSize())
        if (w,h) in self.map:
            self.map[(w,h)].append(img)
        else:
            self.map[(w, h)] = [img]

    def GetImage(self, w, h):
        (w, h) = self.NormalizeSize(w, h)
        if (w,h) in self.map and len(self.map[(w,h)]):
            img = self.map[(w,h)].pop()
            img.Clear()
            return img

        img = wx.Image(w, h, clear=True)
        return img
