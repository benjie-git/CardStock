#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel


class UiTextLabel(UiView):
    def __init__(self, stackView, model=None):
        if not model:
            model = TextLabelModel()
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("label_"))

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

        label = wx.StaticText(parent=stackView, id=wx.ID_ANY, size=(60,20), style=alignment|wx.ST_NO_AUTORESIZE)
        label.SetLabelText(text)
        famimlyName = model.GetProperty("font")
        size = int(model.GetProperty("fontSize"))
        label.SetFont(wx.Font(wx.FontInfo(size).Family(self.FamilyForName(famimlyName))))
        label.SetForegroundColour(model.GetProperty("textColor"))
        return label

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            self.view.SetLabelText(str(self.model.GetProperty(key)))
        elif key == "font" or key == "fontSize":
            famimlyName = self.model.GetProperty("font")
            size = int(self.model.GetProperty("fontSize"))
            self.view.SetFont(wx.Font(wx.FontInfo(size).Family(self.FamilyForName(famimlyName))))
        elif key == "textColor":
            self.view.SetForegroundColour(model.GetProperty(key))
            self.view.Refresh()
        elif key == "alignment":
            self.stackView.SelectUiView(None)
            self.view.Destroy()
            newLabel = self.CreateLabel(self.stackView, self.model)
            self.SetView(newLabel)
            self.stackView.LoadCardAtIndex(self.stackView.cardIndex, reload=True)
            self.stackView.SelectUiView(self)

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
    def __init__(self):
        super().__init__()
        self.type = "textlabel"

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["textColor"] = "black"
        self.properties["font"] = "Helvetica"
        self.properties["fontSize"] = "18"

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["textColor"] = "string"
        self.propertyTypes["font"] = "choice"
        self.propertyTypes["fontSize"] = "int"
        self.propertyChoices["alignment"] = ["Left", "Center", "Right"]
        self.propertyChoices["font"] = ["Default", "Serif", "Sans-Serif", "Mono"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "position", "size"]

    def GetText(self): return self.GetProperty("text")
    def SetText(self, text): self.SetProperty("text", str(text))
    def AppendText(self, text): self.SetProperty("text", self.GetProperty("text") + str(text))
