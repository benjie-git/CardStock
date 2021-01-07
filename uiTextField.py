#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from uiView import UiView, ViewModel


class UiTextField(UiView):
    def __init__(self, page, model=None):
        field = wx.TextCtrl(parent=page, id=wx.ID_ANY, value="TextField", style=wx.TE_PROCESS_ENTER) # wx.TE_MULTILINE

        if not model:
            model = TextFieldModel()
            model.SetProperty("name", page.uiPage.model.GetNextAvailableNameForBase("field_"))

        super().__init__(page, model, field)
        self.model = model

        self.view.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        self.view.Bind(wx.EVT_CHAR, self.OnTextChanged)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            self.view.ChangeValue(str(self.model.GetProperty("text")))

    def SetEditing(self, editing):
        UiView.SetEditing(self, editing)
        if editing:
            self.view.SetEditable(False)
        else:
            self.view.SetEditable(self.model.GetProperty("editable"))

    def OnTextEnter(self, event):
        if not self.isEditing:
            if "OnTextEnter" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnTextEnter", event)
            event.Skip()

    def OnTextChanged(self, event):
        if not self.isEditing:
            if "OnTextChanged" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnTextChanged", event)
            event.Skip()


class TextFieldModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "textfield"

        # Add custom handlers to the top of the list
        handlers = {"OnTextEnter": "", "OnTextChanged": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        self.properties["editable"] = True
        self.properties["text"] = "Text"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "editable", "position", "size"]

    def GetText(self): return self.GetProperty("text")
    def SetText(self, text): self.SetProperty("text", text)
