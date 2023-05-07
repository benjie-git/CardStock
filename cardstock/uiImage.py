# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import wx
import generator
from uiView import *


class UiImage(UiView):
    """
    This class is a controller that coordinates management of an image view, based on data from an ImageModel.
    An image does not use its own wx.Window as a view, but instead draws itself onto the stack view.
    """

    imgCache = {}

    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model, None)
        self.scaledBitmap = None
        self.origImage = self.GetImg(model)

    @classmethod
    def ClearCache(cls, path=None):
        if path:
            if path in cls.imgCache:
                del cls.imgCache[path]
        else:
            cls.imgCache = {}

    def AspectStrToInt(self, str):
        if str == "Center":
            return 0
        elif str == "Stretch":
            return 1
        elif str == "Scale":
            return 3
        else:
            return 3 # Default to Scale

    def GetImg(self, model):
        file = model.GetProperty("file")
        filepath = self.stackManager.resPathMan.GetAbsPath(file)

        if filepath in self.imgCache:
            img = self.imgCache[filepath]
        else:
            if filepath and os.path.exists(filepath):
                img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
                self.imgCache[filepath] = img
            else:
                img = None
        return img

    def MakeScaledBitmap(self):
        img = self.origImage
        if not img:
            return None

        xFlipped = self.model.GetProperty("xFlipped")
        yFlipped = self.model.GetProperty("yFlipped")
        imgSize = img.GetSize()
        viewSize = self.stackManager.view.FromDIP(self.model.GetProperty("size"))
        fit = self.model.GetProperty("fit")

        if xFlipped or yFlipped:
            if xFlipped:
                img = img.Mirror(horizontally=True)
            if yFlipped:
                img = img.Mirror(horizontally=False)

        if fit == "Stretch":
            img = img.Scale(self.stackManager.view.FromDIP(viewSize.width), self.stackManager.view.FromDIP(viewSize.height), quality=wx.IMAGE_QUALITY_HIGH)
        elif fit == "Contain":
            scaleX = viewSize.width / imgSize.width
            scaleY = viewSize.height / imgSize.height
            scale = min(scaleX, scaleY)
            img = img.Scale(max(1, int(imgSize.width * scale)),
                            max(1, int(imgSize.height * scale)), quality=wx.IMAGE_QUALITY_HIGH)
        elif fit == "Fill":
            scaleX = viewSize.width / imgSize.width
            scaleY = viewSize.height / imgSize.height
            scale = max(scaleX, scaleY)
            img = img.Scale(int(imgSize.width * scale),
                            int(imgSize.height * scale), quality=wx.IMAGE_QUALITY_HIGH)
            imgSize = img.GetSize()

        if fit in ["Center", "Fill"]:
            if self.stackManager.view.FromDIP(100) != 100:
                img = img.Scale(self.stackManager.view.FromDIP(imgSize.width),
                                self.stackManager.view.FromDIP(imgSize.height), quality=wx.IMAGE_QUALITY_HIGH)
                imgSize = self.stackManager.view.FromDIP(imgSize)
            offX = 0 if imgSize.Width <= viewSize.Width else self.stackManager.view.ToDIP(int((imgSize.Width - viewSize.Width) / 2))
            offY = 0 if imgSize.Height <= viewSize.Height else self.stackManager.view.ToDIP(int((imgSize.Height - viewSize.Height) / 2))
            w = imgSize.width if imgSize.Width <= viewSize.Width else viewSize.Width
            h = imgSize.height if imgSize.Height <= viewSize.Height else viewSize.Height
            img = img.GetSubImage(wx.Rect(int(offX), int(offY), w, h))

        self.scaledBitmap = img.ConvertToBitmap(32)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)

        if key in ["size", "fit", "file", "xFlipped", "yFlipped"]:
            self.scaledBitmap = None
            self.stackManager.view.Refresh()

        if key == "file":
            self.origImage = self.GetImg(self.model)
            self.scaledBitmap = None
            self.stackManager.view.Refresh()
        elif key == "fit":
            self.stackManager.view.Refresh()

    def ClearCachedData(self):
        self.scaledBitmap = None
        self.origImage = None
        self.stackManager.view.Refresh()

    def Paint(self, gc):
        if self.model.GetProperty("file"):
            if not self.origImage:
                self.origImage = self.GetImg(self.model)
            if self.origImage:
                if not self.scaledBitmap:
                    self.MakeScaledBitmap()

                imgSize = self.scaledBitmap.GetSize()
                viewSize = self.stackManager.view.FromDIP(self.model.GetProperty("size"))
                offX = (viewSize.Width - imgSize.Width) / 2
                offY = (viewSize.Height - imgSize.Height) / 2
                gc.DrawBitmap(self.scaledBitmap, self.stackManager.view.ToDIP(int(offX)), self.stackManager.view.ToDIP(int(offY + imgSize.Height)))

        if self.stackManager.isEditing:
            self.PaintBoundingBox(gc)


class ImageModel(ViewModel):
    """
    This is the model for an Image object.
    """

    minSize = wx.Size(2, 2)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "image"
        self.proxyClass = Image

        self.properties["name"] = "image_1"
        self.properties["file"] = ""
        self.properties["fit"] = "Contain"
        self.properties["rotation"] = 0.0
        self.properties["xFlipped"] = False
        self.properties["yFlipped"] = False

        self.propertyTypes["file"] = "file"
        self.propertyTypes["fit"] = "choice"
        self.propertyTypes["rotation"] = "float"
        self.propertyTypes["xFlipped"] = "bool"
        self.propertyTypes["yFlipped"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "fit", "position", "size", "rotation"]

    def PerformFlips(self, fx, fy, notify=True):
        super().PerformFlips(fx, fy, notify)
        if fx:
            self.SetProperty("xFlipped", not self.GetProperty("xFlipped"), notify=notify)
        if fy:
            self.SetProperty("yFlipped", not self.GetProperty("yFlipped"), notify=notify)


class Image(ViewProxy):
    """
    Image proxy objects are the user-accessible objects exposed to event handler code for image objects.
    """

    @property
    def file(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("file")
    @file.setter
    def file(self, val):
        if not isinstance(val, str):
            raise TypeError("file must be a string")
        model = self._model
        if not model: return
        model.SetProperty("file", val)

    @property
    def fit(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fit")
    @fit.setter
    def fit(self, val):
        if not isinstance(val, str):
            raise TypeError("fit must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fit", val)
