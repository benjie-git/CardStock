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

        container = generator.TransparentWindow(parent.view)
        container.Enable(True)
        self.stackView = stackView
        self.origImage = self.GetImg(model)
        rotatedBitmap = self.RotatedBitmap(model)
        self.imgView = wx.StaticBitmap(container, bitmap=rotatedBitmap)
        self.imgView.Enable(True)
        self.imgView.SetScaleMode(self.AspectStrToInt(model.GetProperty("fit")))
        self.imgView.Show(model.GetProperty("file") != "")
        self.BindEvents(self.imgView)

        super().__init__(parent, stackView, model, container)

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
        if file and self.stackView.filename:
            dir = os.path.dirname(self.stackView.filename)
            file = os.path.join(dir, file)
        if os.path.exists(file):
            img = wx.Image(file, wx.BITMAP_TYPE_ANY)
        else:
            img = wx.Image(20,20, True)
        return img

    def RotatedBitmap(self, model):
        img = self.origImage
        val = float(model.GetProperty("rotation") * -pi/180)  # make positive value rotate clockwise
        img = img.Rotate(val, list(model.GetProperty("size")/2))   # use orignal center
        return img.ConvertToBitmap(32)

    def OnResize(self, event):
        super().OnResize(event)
        self.imgView.SetSize(self.view.GetSize())

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "file":
            self.origImage = self.GetImg(self.model)
            rotatedBitmap = self.RotatedBitmap(model)
            self.imgView.SetBitmap(rotatedBitmap)
            self.imgView.SetSize(self.view.GetSize())
            self.imgView.Show(model.GetProperty(key) != "")
            self.view.Refresh(True)
        elif key == "fit":
            self.imgView.SetScaleMode(self.AspectStrToInt(model.GetProperty(key)))
            self.view.Refresh(True)
        elif key == "rotation":
            if model.GetProperty("file") != "":
                rotatedBitmap = self.RotatedBitmap(model)
                self.imgView.SetBitmap(rotatedBitmap)
                self.imgView.SetSize(self.view.GetSize())
                self.view.Refresh(True)


class ImageModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "image"
        self.proxyClass = ImageProxy

        self.properties["file"] = ""
        self.properties["fit"] = "Scale"
        self.properties["rotation"] = 0

        self.propertyTypes["file"] = "string"
        self.propertyTypes["fit"] = "choice"
        self.propertyChoices["fit"] = ["Center", "Stretch", "Fill"]
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
