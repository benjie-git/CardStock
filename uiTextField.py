#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from uiView import UiView, ViewModel


class UiTextField(UiView):
    def __init__(self, page, model=None):
        field = self.CreateField(page, model)

        if not model:
            model = TextFieldModel()
            model.SetProperty("name", page.uiPage.model.GetNextAvailableNameForBase("field_"))

        super().__init__(page, model, field)

    def CreateField(self, page, model):
        if model:
            text = model.GetProperty("text")
            alignment = wx.TE_LEFT
            if model.GetProperty("alignment") == "Right":
                alignment = wx.TE_RIGHT
            elif model.GetProperty("alignment") == "Center":
                alignment = wx.TE_CENTER
        else:
            text = "Text"
            alignment = wx.TEXT_ALIGNMENT_LEFT

        field = wx.TextCtrl(parent=page, id=wx.ID_ANY, value="TextField", style=wx.TE_PROCESS_ENTER|alignment) # wx.TE_MULTILINE
        field.SetLabelText(text)
        return field

    def SetView(self, view):
        super().SetView(view)
        view.ChangeValue(self.model.GetProperty("text"))
        view.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        view.Bind(wx.EVT_CHAR, self.OnTextChanged)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            self.view.ChangeValue(str(self.model.GetProperty(key)))
        elif key == "alignment":
            self.page.SelectUiView(None)
            self.view.Destroy()
            newField = self.CreateField(self.page, self.model)
            self.SetView(newField)
            self.page.SelectUiView(self)

    def SetEditing(self, editing):
        UiView.SetEditing(self, editing)
        if editing:
            self.view.SetEditable(False)
        else:
            self.view.SetEditable(self.model.GetProperty("editable"))

    def OnTextEnter(self, event):
        if not self.isEditing:
            if "OnTextEnter" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnTextEnter", event)
            event.Skip()

    def OnTextChanged(self, event):
        if not self.isEditing:
            if "OnTextChanged" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnTextChanged", event)
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
        self.properties["alignment"] = "Left"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "editable", "position", "size"]

    def GetText(self): return self.GetProperty("text")
    def SetText(self, text): self.SetProperty("text", text)
