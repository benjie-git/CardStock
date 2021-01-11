#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from uiView import UiView, ViewModel


class UiTextLabel(UiView):
    def __init__(self, stackView, model=None):
        if not model:
            model = TextLabelModel()
            model.SetProperty("name", stackView.uiPage.model.GetNextAvailableNameForBase("label_"))

        label = self.CreateLabel(stackView, model)
        label.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        super().__init__(stackView, model, label)

    def CreateLabel(self, stackView, model):
        if model:
            text = model.GetProperty("text")
            alignment = wx.ALIGN_LEFT
            if model.GetProperty("alignment") == "Right":
                alignment = wx.ALIGN_RIGHT
            elif model.GetProperty("alignment") == "Center":
                alignment = wx.ALIGN_CENTER
        else:
            text = "Text"
            alignment = wx.ALIGN_LEFT

        label = wx.StaticText(parent=stackView, id=wx.ID_ANY, style=alignment)
        label.SetLabelText(text)
        return label

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            self.view.SetLabelText(str(self.model.GetProperty(key)))
        elif key == "alignment":
            self.stackView.SelectUiView(None)
            self.view.Destroy()
            newLabel = self.CreateLabel(self.stackView, self.model)
            self.SetView(newLabel)
            self.stackView.SelectUiView(self)


class TextLabelModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "textlabel"

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyChoices["alignment"] = ["Left", "Center", "Right"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "position", "size"]

    def GetText(self): return self.GetProperty("text")
    def SetText(self, text): self.SetProperty("text", str(text))
    def AppendText(self, text): self.SetProperty("text", self.GetProperty("text") + str(text))
