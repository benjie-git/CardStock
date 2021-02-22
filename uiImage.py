#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import os
import wx
import generator
from math import pi
from uiView import *


class UiImage(UiView):

    imgCache = {}

    def __init__(self, parent, stackView, model=None):
        if not model:
            model = ImageModel(stackView)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("image_"), False)

        super().__init__(parent, stackView, model, None)
        self.rotatedBitmap = None
        self.origImage = self.GetImg(model)

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
        if file in self.imgCache:
            img = self.imgCache[file]
        else:
            if file and self.stackView.filename:
                fileDir = os.path.dirname(self.stackView.filename)
                path = os.path.join(fileDir, file)
            else:
                path = file

            if os.path.exists(path):
                img = wx.Image(path, wx.BITMAP_TYPE_ANY)
                self.imgCache[file] = img
            else:
                img = None
        return img

    def MakeScaledAndRotatedBitmap(self):
        img = self.origImage
        if not img:
            return None

        rot = self.model.GetProperty("rotation")
        imgSize = img.GetSize()
        viewSize = self.model.GetProperty("size")
        fit = self.model.GetProperty("fit")

        if rot != 0:
            val = float(rot * -pi/180)  # make positive value rotate clockwise
            img = img.Rotate(val, list(img.GetSize()/2))   # use original center
            imgSize = img.GetSize()

        if fit == "Stretch":
            img = img.Scale(viewSize.width, viewSize.height, quality=wx.IMAGE_QUALITY_HIGH)
        elif fit == "Fit":
            scaleX = viewSize.width / imgSize.width
            scaleY = viewSize.height / imgSize.height
            scale = min(scaleX, scaleY)
            img = img.Scale(imgSize.width * scale, imgSize.height * scale, quality=wx.IMAGE_QUALITY_HIGH)
        elif fit == "Fill":
            scaleX = viewSize.width / imgSize.width
            scaleY = viewSize.height / imgSize.height
            scale = max(scaleX, scaleY)
            img = img.Scale(imgSize.width * scale, imgSize.height * scale, quality=wx.IMAGE_QUALITY_HIGH)
            imgSize = img.GetSize()

        if fit in ["Center", "Fill"]:
            offX = 0 if imgSize.Width <= viewSize.Width else ((imgSize.Width - viewSize.Width) / 2)
            offY = 0 if imgSize.Height <= viewSize.Height else ((imgSize.Height - viewSize.Height) / 2)
            w = imgSize.width if imgSize.Width <= viewSize.Width else viewSize.Width
            h = imgSize.height if imgSize.Height <= viewSize.Height else viewSize.Height
            img = img.GetSubImage(wx.Rect(offX, offY, w, h))

        self.rotatedBitmap = img.ConvertToBitmap(32)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)

        if key in ["size", "rotation", "fit", "file"]:
            self.rotatedBitmap = None

        if key == "file":
            self.origImage = self.GetImg(self.model)
            self.rotatedBitmap = None
            self.stackView.Refresh(True, self.model.GetRefreshFrame())
        elif key == "fit":
            self.stackView.Refresh(True, self.model.GetRefreshFrame())
        elif key == "rotation":
            if model.GetProperty("file") != "":
                self.stackView.Refresh(True, self.model.GetRefreshFrame())

    def Paint(self, gc):
        if self.origImage:
            if not self.rotatedBitmap:
                self.MakeScaledAndRotatedBitmap()
            r = self.model.GetAbsoluteFrame()

            imgSize = self.rotatedBitmap.GetSize()
            viewSize = r.Size
            offX = 0 if (imgSize.Width >= viewSize.Width) else ((viewSize.Width - imgSize.Width) / 2)
            offY = 0 if (imgSize.Height >= viewSize.Height) else ((viewSize.Height - imgSize.Height) / 2)
            gc.DrawBitmap(self.rotatedBitmap, r.Left + offX, r.Top + offY)
        super().Paint(gc)


class ImageModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "image"
        self.proxyClass = ImageProxy

        self.properties["file"] = ""
        self.properties["fit"] = "Fill"
        self.properties["rotation"] = 0

        self.propertyTypes["file"] = "string"
        self.propertyTypes["fit"] = "choice"
        self.propertyChoices["fit"] = ["Center", "Stretch", "Fit", "Fill"]
        self.propertyTypes["rotation"] = "int"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "fit", "rotation", "position", "size"]

    def SetProperty(self, key, value, notify=True):
        if key == "rotation":
            value = value % 360
        super().SetProperty(key, value, notify)

class ImageProxy(ViewProxy):
    @property
    def file(self):
        return self._model.GetProperty("file")
    @file.setter
    def file(self, val):
        self._model.SetProperty("file", val)

    @property
    def rotation(self):
        return self._model.GetProperty("rotation")
    @rotation.setter
    def rotation(self, val):
        self._model.SetProperty("rotation", val)

    @property
    def fit(self):
        return self._model.GetProperty("fit")
    @fit.setter
    def fit(self, val):
        self._model.SetProperty("fit", val)

    def AnimateRotation(self, duration, endRotation, onFinished=None):
        origRotation = self.rotation
        if endRotation != origRotation:
            offset = endRotation - origRotation
            def f(progress):
                self.rotation = origRotation + offset * progress
            self._model.AddAnimation("rotation", duration, f, onFinished)
        else:
            self._model.AddAnimation("rotation", duration, None, onFinished)
