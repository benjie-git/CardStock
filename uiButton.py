#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *


class UiButton(UiView):
    def __init__(self, parent, stackManager, model=None):
        if not model:
            model = ButtonModel(stackManager)
            model.SetProperty("name", stackManager.uiCard.model.GetNextAvailableNameInCard("button_"), False)

        self.stackManager = stackManager
        self.button = self.CreateButton(stackManager, model)

        super().__init__(parent, stackManager, model, self.button)

    def GetCursor(self):
        return wx.CURSOR_HAND

    def BindEvents(self, view):
        if view == self.view:
            super().BindEvents(self.button)

    def CreateButton(self, stackManager, model):
        button = wx.Button(parent=stackManager.view, label="Button",
                         style=(wx.BORDER_DEFAULT if model.GetProperty("border") else wx.BORDER_NONE))
        button.SetLabel(model.GetProperty("title"))
        button.Bind(wx.EVT_BUTTON, self.OnButton)
        button.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        button.SetCursor(wx.Cursor(self.GetCursor()))
        return button

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "title":
            self.button.SetLabel(str(self.model.GetProperty(key)))
        elif key == "border":
            self.stackManager.SelectUiView(None)
            self.doNotCache = True
            self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)
            self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(self.model))

    def OnKeyDown(self, event):
        if event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            self.OnButton(event)
        event.Skip()

    def OnButton(self, event):
        if not self.stackManager.isEditing:
            if self.stackManager.runner and self.model.GetHandler("OnClick"):
                self.stackManager.runner.RunHandler(self.model, "OnClick", event)


class ButtonModel(ViewModel):
    def __init__(self, stackManager):
        super().__init__(stackManager)
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

    @property
    def border(self):
        return self._model.GetProperty("border")
    @border.setter
    def border(self, val):
        self._model.SetProperty("border", val)

    def DoClick(self):
        if self._model.stackManager.runner:
            self._model.stackManager.runner.RunHandler(self._model, "OnClick", None)
