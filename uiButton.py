#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel


class UiButton(UiView):
    def __init__(self, parent, stackView, model=None):
        if not model:
            model = ButtonModel(stackView)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("button_"), False)

        button = self.CreateButton(parent, model)

        button.SetCursor(wx.Cursor())
        super().__init__(parent, stackView, model, button)

    def CreateButton(self, parent, model):
        return wx.Button(parent=parent.view, label="Button",
                         style=(wx.BORDER_DEFAULT if model.GetProperty("border") else wx.BORDER_NONE))

    def SetView(self, view):
        super().SetView(view)
        view.SetLabel(self.model.GetProperty("title"))
        view.Bind(wx.EVT_BUTTON, self.OnButton)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "title":
            self.view.SetLabel(str(self.model.GetProperty(key)))
        elif key == "border":
            self.stackView.SelectUiView(None)
            self.view.Destroy()
            newButton = self.CreateButton(self.parent, self.model)
            self.SetView(newButton)
            self.stackView.LoadCardAtIndex(self.stackView.cardIndex, reload=True)
            self.stackView.SelectUiView(self)


    def OnButton(self, event):
        if not self.stackView.isEditing:
            if self.stackView.runner and "OnClick" in self.model.handlers:
                self.stackView.runner.RunHandler(self.model, "OnClick", event)


class ButtonModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "button"

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

    # --------- User-accessible view methods -----------

    @property
    def title(self):
        return self.GetProperty("title")
    @title.setter
    def title(self, val):
        self.SetProperty("title", val)

    def DoClick(self):
        if self.stackView.runner:
            self.stackView.runner.RunHandler(self, "OnClick", None)
