#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *


class UiButton(UiView):
    def __init__(self, parent, stackView, model=None):
        if not model:
            model = ButtonModel(stackView)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("button_"), False)

        container = generator.TransparentWindow(parent.view)
        container.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        container.Enable(True)
        container.SetCursor(wx.Cursor(self.GetCursor()))

        self.stackView = stackView
        self.button = self.CreateButton(container, model)

        super().__init__(parent, stackView, model, container)

    def CreateButton(self, parent, model):
        button = wx.Button(parent=parent, label="Button",
                         style=(wx.BORDER_DEFAULT if model.GetProperty("border") else wx.BORDER_NONE))
        button.SetLabel(model.GetProperty("title"))
        button.Bind(wx.EVT_BUTTON, self.OnButton)
        button.SetCursor(wx.Cursor(self.GetCursor()))
        self.BindEvents(button)
        return button

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "title":
            self.button.SetLabel(str(self.model.GetProperty(key)))
        elif key == "border":
            self.stackView.SelectUiView(None)
            self.view.RemoveChild(self.button)
            self.button.Destroy()
            self.button = None
            self.doNotCache = True
            self.stackView.LoadCardAtIndex(self.stackView.cardIndex, reload=True)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.model))

    def OnResize(self, event):
        super().OnResize(event)
        if self.button:
            if wx.Platform == '__WXMAC__':
                self.button.SetPosition([0, 0])
                self.button.SetSize(self.view.GetSize() - [3,2])
            else:
                self.button.SetSize(self.view.GetSize())

    def OnFocus(self, event):
        self.field.SetFocus()

    def OnButton(self, event):
        if not self.stackView.isEditing:
            if self.stackView.runner and self.model.GetHandler("OnClick"):
                self.stackView.runner.RunHandler(self.model, "OnClick", event)


class ButtonModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "button"
        self.proxyClass = ProxyButton

        # Add custom handlers to the top of the list
        handlers = {"OnClick": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        self.properties["title"] = "Button"
        self.properties["border"] = True
        self.propertyTypes["title"] = "string"
        self.propertyTypes["border"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "title", "border", "position", "size"]


class ProxyButton(ViewProxy):
    @property
    def title(self):
        return self._model.GetProperty("title")
    @title.setter
    def title(self, val):
        self._model.SetProperty("title", val)

    def DoClick(self):
        if self._model.stackView.runner:
            self._model.stackView.runner.RunHandler(self._model, "OnClick", None)
