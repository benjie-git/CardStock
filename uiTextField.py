#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *
import wx.stc as stc


class UiTextField(UiView):
    def __init__(self, parent, stackView, model=None):
        if not model:
            model = TextFieldModel(stackView)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("field_"), False)

        field = self.CreateField(parent, stackView, model)

        super().__init__(parent, stackView, model, field)

    def CreateField(self, parent, stackView, model):
        text = model.GetProperty("text")
        alignment = wx.TE_LEFT
        if model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        if model.GetProperty("multiline"):
            field = stc.StyledTextCtrl(parent=parent.view, style=alignment | wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
            field.SetUseHorizontalScrollBar(False)
            field.SetWrapMode(stc.STC_WRAP_WORD)
            field.SetMarginWidth(1, 0)
            field.ChangeValue(text)
            field.Bind(stc.EVT_STC_CHANGE, self.OnTextChanged)
            field.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        else:
            field = wx.TextCtrl(parent=parent.view, id=wx.ID_ANY, value="TextField", style=wx.TE_PROCESS_ENTER | alignment)
            field.Bind(wx.EVT_TEXT, self.OnTextChanged)
            field.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
            field.ChangeValue(text)

        if stackView.isEditing:
            field.SetEditable(False)
        else:
            field.SetEditable(model.GetProperty("editable"))
        return field

    def SetView(self, view):
        super().SetView(view)
        view.ChangeValue(self.model.GetProperty("text"))

    def GetCursor(self):
        if self.stackView.isEditing:
            return wx.CURSOR_HAND
        else:
            return None

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
            self.view.Refresh()
        elif key == "alignment" or key == "multiline":
            self.stackView.SelectUiView(None)
            self.view.Destroy()
            newField = self.CreateField(self.parent, self.stackView, self.model)
            self.SetView(newField)
            self.stackView.LoadCardAtIndex(self.stackView.cardIndex, reload=True)
            self.stackView.SelectUiView(self)
        elif key == "selectAll":
            self.view.SelectAll()

    def OnTextEnter(self, event):
        if not self.stackView.isEditing:
            if self.stackView.runner and self.model.GetHandler("OnTextEnter"):
                self.stackView.runner.RunHandler(self.model, "OnTextEnter", event)

    def OnTextChanged(self, event):
        if not self.stackView.isEditing:
            self.model.SetProperty("text", self.view.GetValue(), notify=False)
            if self.stackView.runner and self.model.GetHandler("OnTextChanged"):
                self.stackView.runner.RunHandler(self.model, "OnTextChanged", event)


class TextFieldModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "textfield"
        self.proxyClass = TextFieldProxy

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


class TextFieldProxy(ViewProxy):
    @property
    def text(self):
        return self._model.GetProperty("text")
    @text.setter
    def text(self, val):
        self._model.SetProperty("text", val)

    def SelectAll(self): self._model.Notify("selectAll")

    def DoEnter(self):
        if self._model.stackView.runner:
            self._model.stackView.runner.RunHandler(self._model, "OnTextEnter", None)
