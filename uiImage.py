#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import os
import wx
import generator
from uiView import UiView, ViewModel

class UiImage(UiView):
    def __init__(self, parent, stackView, model=None):
        if not model:
            model = ImageModel()
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("image_"), False)

        img = self.GetImg(model)
        container = generator.TransparentWindow(parent.view)
        container.Enable(True)
        self.imgView = wx.StaticBitmap(container, bitmap=img)
        self.imgView.Enable(True)
        self.imgView.SetScaleMode(self.AspectStrToInt(model.GetProperty("fit")))
        container.SetBackgroundColour(model.GetProperty("bgColor"))
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
            bmp = wx.Image(100,100, True).ConvertToBitmap()
        return bmp

    def OnResize(self, event):
        super().OnResize(event)
        self.imgView.SetSize(self.view.GetSize())
        event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "file":
            img = self.GetImg(self.model)
            self.imgView.SetBitmap(img)
            self.imgView.SetSize(self.view.GetSize())
            self.imgView.Show(model.GetProperty(key) != "")
        elif key == "fit":
            self.imgView.SetScaleMode(self.AspectStrToInt(model.GetProperty(key)))
        elif key == "bgColor":
            self.view.SetBackgroundColour(model.GetProperty(key))
            self.view.Refresh()


class ImageModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "image"

        self.properties["file"] = ""
        self.properties["fit"] = "Scale"
        self.properties["bgColor"] = ""

        self.propertyTypes["file"] = "string"
        self.propertyTypes["fit"] = "choice"
        self.propertyTypes["bgColor"] = "color"
        self.propertyChoices["fit"] = ["Center", "Stretch", "Fill"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "fit", "bgColor", "position", "size"]

    def GetFile(self): return self.GetProperty("file")
    def SetFile(self, text): self.SetProperty("file", text)

    def GetBgColor(self): return self.GetProperty("bgColor")
    def SetBgColor(self, colorStr): self.SetProperty("bgColor", colorStr)
