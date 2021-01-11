#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from uiView import UiView, ViewModel
import wx.stc as stc


class UiTextField(UiView):
    def __init__(self, stackView, model=None):
        if not model:
            model = TextFieldModel()
            model.SetProperty("name", stackView.uiPage.model.GetNextAvailableNameForBase("field_"))

        field = self.CreateField(stackView, model)

        super().__init__(stackView, model, field)

    def CreateField(self, stackView, model):
        text = model.GetProperty("text")
        alignment = wx.TE_LEFT
        if model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        if model.GetProperty("multiline"):
            field = stc.StyledTextCtrl(parent=stackView, style=alignment | wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
            field.SetUseHorizontalScrollBar(False)
            field.SetMarginWidth(1, 0)
            field.ChangeValue(text)
            field.Bind(stc.EVT_STC_CHANGE, self.OnTextChanged)
        else:
            field = wx.TextCtrl(parent=stackView, id=wx.ID_ANY, value="TextField", style=wx.TE_PROCESS_ENTER | alignment)
            field.ChangeValue(text)
        return field

    def SetView(self, view):
        super().SetView(view)
        view.ChangeValue(self.model.GetProperty("text"))
        view.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        view.Bind(wx.EVT_TEXT, self.OnTextChanged)

    def OnResize(self, event):
        super().OnResize(event)
        if self.model.GetProperty("multiline"):
            self.view.SetScrollWidth(self.view.GetSize().Width-6)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            wasEditable = self.view.IsEditable()
            if not wasEditable:
                self.view.SetEditable(True)
            self.view.ChangeValue(str(self.model.GetProperty(key)))
            self.view.SetEditable(wasEditable)
        elif key == "alignment" or key == "multiline":
            self.stackView.SelectUiView(None)
            self.view.Destroy()
            newField = self.CreateField(self.stackView, self.model)
            self.SetView(newField)
            self.stackView.SelectUiView(self)

    def SetEditing(self, editing):
        UiView.SetEditing(self, editing)
        if editing:
            self.view.SetEditable(False)
        else:
            self.view.SetEditable(self.model.GetProperty("editable"))

    def OnTextEnter(self, event):
        if not self.isEditing:
            if self.model.runner and "OnTextEnter" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnTextEnter", event)
            event.Skip()

    def OnTextChanged(self, event):
        if not self.isEditing:
            self.model.SetProperty("text", self.view.GetValue())
            if self.model.runner and "OnTextChanged" in self.model.handlers:
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

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["editable"] = True
        self.properties["multiline"] = False

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["editable"] = "bool"
        self.propertyTypes["multiline"] = "bool"
        self.propertyChoices["alignment"] = ["Left", "Center", "Right"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "editable", "multiline", "position", "size"]

    def GetText(self): return self.GetProperty("text")
    def SetText(self, text): self.SetProperty("text", str(text))
    def AppendText(self, text): self.SetProperty("text", self.GetProperty("text") + str(text))
