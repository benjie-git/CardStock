#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import os
import wx
import generator
from math import pi
from uiView import *


class UiImage(UiView):
    def __init__(self, parent, stackView, model=None):
        if not model:
            model = ImageModel(stackView)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("image_"), False)

        container = wx.Window(parent.view)
        container.Enable(True)
        container.SetBackgroundColour(model.GetProperty("bgColor"))
        self.origBitmap = self.GetImg(model)
        rotatedBitmap = self.RotatedBitmap(model)
        self.imgView = wx.StaticBitmap(container, bitmap=rotatedBitmap)
        self.imgView.Enable(True)
        self.imgView.SetBackgroundColour(None)
        self.imgView.SetScaleMode(self.AspectStrToInt(model.GetProperty("fit")))
        self.imgView.Show(model.GetProperty("file") != "")

        super().__init__(parent, stackView, model, container)
        self.BindEvents(self.imgView)

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
        if os.path.exists(file):
            bmp = wx.Image(file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        else:
            bmp = wx.Image(20,20, True).ConvertToBitmap()
        return bmp

    def RotatedBitmap(self, model):
        img = self.origBitmap.ConvertToImage()
        val = float(model.GetProperty("rotation") * -pi/180)  # make positive value rotate clockwise
        img = img.Rotate(val, list(model.GetProperty("size")/2))   # use orignal center
        # img = img.Scale(self._W, self._H)  ## use original size
        return img.ConvertToBitmap()

    def OnResize(self, event):
        super().OnResize(event)
        self.imgView.SetSize(self.view.GetSize())
        event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "file":
            self.origBitmap = self.GetImg(self.model)
            rotatedBitmap = self.RotatedBitmap(model)
            self.imgView.SetBitmap(rotatedBitmap)
            self.imgView.SetSize(self.view.GetSize())
            self.imgView.Show(model.GetProperty(key) != "")
        elif key == "fit":
            self.imgView.SetScaleMode(self.AspectStrToInt(model.GetProperty(key)))
        elif key == "bgColor":
            self.view.SetBackgroundColour(model.GetProperty(key))
            self.view.Refresh()
        elif key == "rotation":
            if model.GetProperty("file") != "":
                rotatedBitmap = self.RotatedBitmap(model)
                self.imgView.SetBitmap(rotatedBitmap)
                self.imgView.SetSize(self.view.GetSize())


class ImageModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "image"
        self.proxyClass = ImageProxy

        self.properties["file"] = ""
        self.properties["fit"] = "Scale"
        self.properties["bgColor"] = ""
        self.properties["rotation"] = 0

        self.propertyTypes["file"] = "string"
        self.propertyTypes["fit"] = "choice"
        self.propertyTypes["bgColor"] = "color"
        self.propertyChoices["fit"] = ["Center", "Stretch", "Fill"]
        self.propertyTypes["rotation"] = "int"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "fit", "bgColor", "rotation", "position", "size"]


class ImageProxy(ViewProxy):
    @property
    def file(self):
        return self._model.GetProperty("file")
    @file.setter
    def file(self, val):
        self._model.SetProperty("file", val)

    @property
    def bgColor(self):
        return self._model.GetProperty("bgColor")
    @bgColor.setter
    def bgColor(self, val):
        self._model.SetProperty("bgColor", val)

    @property
    def rotation(self):
        return self._model.GetProperty("rotation")
    @rotation.setter
    def rotation(self, val):
        self._model.SetProperty("rotation", val)
