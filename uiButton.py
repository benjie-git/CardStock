#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from uiView import UiView, ViewModel


class UiButton(UiView):
    def __init__(self, page, model=None):
        button = wx.Button(parent=page, id=wx.ID_ANY, label="Button")

        if not model:
            model = ButtonModel()
            model.SetProperty("name", page.uiPage.model.GetNextAvailableNameForBase("button_"))

        super().__init__(page, model, button)

        self.view.SetLabel(model.GetProperty("title"))
        self.view.Bind(wx.EVT_BUTTON, self.OnButton)


    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "title":
            self.view.SetLabel(str(self.model.GetProperty("title")))

    def OnButton(self, event):
        if not self.isEditing:
            if "OnClick" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnClick", event)
            event.Skip()


class ButtonModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "button"

        # Add custom handlers to the top of the list
        handlers = {"OnClick": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        self.properties["title"] = "Button"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "title", "position", "size"]

    def GetTitle(self): return self.GetProperty("title")
    def SetTitle(self, text): self.SetProperty("title", text)
    def GetText(self): return self.GetProperty("title")
    def SetText(self, text): self.SetProperty("title", text)
