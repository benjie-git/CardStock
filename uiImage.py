#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import os
import wx
from uiView import UiView, ViewModel

class UiImage(UiView):
    def __init__(self, page, model=None):
        if not model:
            model = ImageModel()
            model.SetProperty("name", page.uiPage.model.GetNextAvailableNameForBase("image_"))

        img = self.GetImg(model)
        container = wx.Window(page)
        container.Enable(True)
        self.imgView = wx.StaticBitmap(container, bitmap=img)
        self.imgView.Enable(True)
        self.imgView.SetScaleMode(3)

        super().__init__(page, model, container)
        self.BindEvents(self.imgView)

    def GetImg(self, model):
        file = model.GetProperty("file")
        if os.path.exists(file):
            img = wx.Image(file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        else:
            img = wx.Image(100,100, True).ConvertToBitmap()
        return img

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


class ImageModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "image"

        self.properties["file"] = ""

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "position", "size"]

    def GetFile(self): return self.GetProperty("file")
    def SetFile(self, text): self.SetProperty("file", text)
