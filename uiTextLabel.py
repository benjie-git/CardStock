#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *


class UiTextLabel(UiView):
    def __init__(self, parent, stackView, model=None):
        if not model:
            model = TextLabelModel(stackView)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("label_"), False)

        container = generator.TransparentWindow(parent.view)
        container.Enable(True)

        self.stackView = stackView
        self.label = self.CreateLabel(container, stackView, model)

        super().__init__(parent, stackView, model, container)

    def CreateLabel(self, parent, stackView, model):
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

        label = wx.StaticText(parent=parent, size=(60,20),
                              style=alignment|wx.ST_NO_AUTORESIZE)
        label.SetLabelText(text)
        famimlyName = model.GetProperty("font")
        size = int(model.GetProperty("fontSize"))
        label.SetFont(wx.Font(wx.FontInfo(size).Family(self.FamilyForName(famimlyName))))
        label.SetForegroundColour(model.GetProperty("textColor"))
        label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.BindEvents(label)
        return label

    def OnResize(self, event):
        super().OnResize(event)
        self.label.SetSize(self.view.GetSize())

        self.label.SetLabel(self.model.GetProperty("text"))
        self.label.Wrap(self.view.GetSize().Width)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            self.label.SetLabelText(str(self.model.GetProperty(key)))
        elif key == "font" or key == "fontSize":
            famimlyName = self.model.GetProperty("font")
            size = int(self.model.GetProperty("fontSize"))
            self.label.SetFont(wx.Font(wx.FontInfo(size).Family(self.FamilyForName(famimlyName))))
        elif key == "textColor":
            self.label.SetForegroundColour(model.GetProperty(key))
            self.label.Refresh(True)
        elif key == "alignment":
            self.stackView.SelectUiView(None)
            self.view.RemoveChild(self.label)
            self.label.Destroy()
            self.label = None
            self.doNotCache = True
            self.stackView.LoadCardAtIndex(self.stackView.cardIndex, reload=True)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(self.model))

    def FamilyForName(self, name):
        if name == "Serif":
            return wx.FONTFAMILY_ROMAN
        if name == "Sans-Serif":
            return wx.FONTFAMILY_SWISS
        if name == "Fancy":
            return wx.FONTFAMILY_DECORATIVE
        if name == "Script":
            return wx.FONTFAMILY_SCRIPT
        if name == "Modern":
            return wx.FONTFAMILY_MODERN
        if name == "Mono":
            return wx.FONTFAMILY_TELETYPE
        return wx.FONTFAMILY_DEFAULT


class TextLabelModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "textlabel"
        self.proxyClass = TextLabelProxy

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["textColor"] = "black"
        self.properties["font"] = "Default"
        self.properties["fontSize"] = "18"

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["textColor"] = "color"
        self.propertyTypes["font"] = "choice"
        self.propertyTypes["fontSize"] = "int"
        self.propertyChoices["alignment"] = ["Left", "Center", "Right"]
        self.propertyChoices["font"] = ["Default", "Serif", "Sans-Serif", "Mono"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "position", "size"]


class TextLabelProxy(ViewProxy):
    @property
    def text(self):
        return self._model.GetProperty("text")
    @text.setter
    def text(self, val):
        self._model.SetProperty("text", val)

    @property
    def textColor(self):
        return self._model.GetProperty("textColor")
    @textColor.setter
    def textColor(self, val):
        self._model.SetProperty("textColor", val)
