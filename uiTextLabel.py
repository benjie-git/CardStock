#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *


class UiTextLabel(UiView):
    def __init__(self, parent, stackManager, model=None):
        if not model:
            model = TextLabelModel(stackManager)
            model.SetProperty("name", stackManager.uiCard.model.GetNextAvailableNameInCard("label_"), False)

        self.stackManager = stackManager
        self.label = self.CreateLabel(stackManager, model)

        super().__init__(parent, stackManager, model, self.label)

    def CreateLabel(self, stackManager, model):
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

        label = wx.StaticText(parent=stackManager.view, size=(60,20),
                              style=alignment|wx.ST_NO_AUTORESIZE)
        label.SetLabelText(text)
        familyName = model.GetProperty("font")
        platformScale = 1.4 if (wx.Platform == '__WXMAC__') else 1.0
        size = int(model.GetProperty("fontSize")) * platformScale
        label.SetFont(wx.Font(wx.FontInfo(size).Family(self.FamilyForName(familyName))))
        label.SetForegroundColour(model.GetProperty("textColor"))
        label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        return label

    def BindEvents(self, view):
        if view == self.view:
            super().BindEvents(self.label)

    def OnResize(self, event):
        self.label.SetLabel(self.model.GetProperty("text"))
        self.label.Wrap(self.view.GetSize().Width)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            self.label.SetLabelText(str(self.model.GetProperty(key)))
            self.OnResize(None)
        elif key == "font" or key == "fontSize":
            familyName = self.model.GetProperty("font")
            platformScale = 1.4 if (wx.Platform == '__WXMAC__') else 1.0
            size = int(model.GetProperty("fontSize") * platformScale)
            self.label.SetFont(wx.Font(wx.FontInfo(size).Family(self.FamilyForName(familyName))))
        elif key == "textColor":
            self.label.SetForegroundColour(model.GetProperty(key))
            self.label.Refresh(True)
        elif key == "alignment":
            self.stackManager.SelectUiView(None)
            self.doNotCache = True
            self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)
            self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(self.model))

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
    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textlabel"
        self.proxyClass = TextLabelProxy

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["textColor"] = "black"
        self.properties["font"] = "Default"
        self.properties["fontSize"] = 18

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
        self._model.SetProperty("text", str(val))

    @property
    def alignment(self):
        return self._model.GetProperty("alignment")
    @alignment.setter
    def alignment(self, val):
        self._model.SetProperty("alignment", val)

    @property
    def textColor(self):
        return self._model.GetProperty("textColor")
    @textColor.setter
    def textColor(self, val):
        self._model.SetProperty("textColor", val)

    @property
    def font(self):
        return self._model.GetProperty("font")
    @font.setter
    def font(self, val):
        self._model.SetProperty("font", val)

    @property
    def fontSize(self):
        return self._model.GetProperty("fontSize")
    @fontSize.setter
    def fontSize(self, val):
        self._model.SetProperty("fontSize", val)

    def AnimateTextColor(self, duration, endVal, onFinished=None):
        origVal = wx.Colour(self.textColor)
        endVal = wx.Colour(endVal)
        if origVal.IsOk() and endVal.IsOk() and endVal != origVal:
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            endParts = [endVal.Red(), endVal.Green(), endVal.Blue(), endVal.Alpha()]
            offsets = [endParts[i]-origParts[i] for i in range(4)]
            def f(progress):
                self.textColor = [origParts[i]+offsets[i]*progress for i in range(4)]
            self._model.AddAnimation("textColor", duration, f, onFinished)
        else:
            self._model.AddAnimation("textColor", duration, None, onFinished)
