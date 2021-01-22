#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel
from uiButton import ButtonModel
from uiTextField import TextFieldModel
from uiTextLabel import TextLabelModel
from uiImage import ImageModel
from uiShape import UiShape, ShapeModel


class UiCard(UiView):
    def __init__(self, stackView, model):
        if not model.GetProperty("name"):
            model.SetProperty("name", model.GetNextAvailableNameInCard("card_"))

        super().__init__(stackView, model, stackView)
        self.cursor = None
        self.stackView.stackModel.SetProperty("size", self.view.GetSize())
        self.view.SetBackgroundColour(self.model.GetProperty("bgColor"))

    def SetView(self, view):
        super().SetView(view)
        self.model.SetProperty("size", self.view.GetSize())
        self.view.SetBackgroundColour(self.model.GetProperty("bgColor"))

    def SetModel(self, model):
        super().SetModel(model)
        if self.view:
            self.view.SetBackgroundColour(self.model.GetProperty("bgColor"))

    def OnResize(self, event):
        super().OnResize(event)
        self.stackView.stackModel.SetProperty("size", self.view.GetSize())

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "name":
            self.stackView.designer.UpdateCardList()
        elif key == "bgColor":
            self.view.SetBackgroundColour(model.GetProperty(key))
            self.view.Refresh()

    def OnKeyDown(self, event):
        if self.model.runner and "OnKeyDown" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnKeyDown", event)

    def OnKeyUp(self, event):
        if self.model.runner and "OnKeyUp" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnKeyUp", event)

    def OnIdle(self, event):
        if self.model.runner and "OnIdle" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnIdle", event)
        for m in self.model.childModels:
            if m.runner and "OnIdle" in m.handlers:
                m.runner.RunHandler(m, "OnIdle", event)


class CardModel(ViewModel):
    minSize = (200, 200)

    def __init__(self):
        super().__init__()
        self.type = "card"
        self.stackModel = None  # For setting stack size

        # Add custom handlers to the top of the list
        handlers = {"OnShowCard": "", "OnHideCard": "","OnIdle": "", "OnKeyDown": "", "OnKeyUp": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        # Custom property order and mask for the inspector
        self.properties["bgColor"] = "white"
        self.propertyKeys = ["name", "bgColor", "stackSize"]
        self.propertyTypes["stackSize"] = "point"
        self.propertyTypes["bgColor"] = "color"

        self.childModels = []

    def SetProperty(self, key, value, notify=True):
        if key == "stackSize":
            self.stackModel.SetProperty("size", value, notify)
        else:
            super().SetProperty(key, value, notify)

    def GetProperty(self, key):
        if key == "stackSize":
            return self.stackModel.GetProperty("size")
        else:
            return super().GetProperty(key)

    def GetHandlers(self):
        h = {"OnStackStart": ""}
        for k,v in self.handlers.items():
            h[k] = v
        return h

    def GetHandler(self, key):
        if key == "OnStackStart":
            return self.stackModel.GetHandler(key)
        else:
            return super().GetHandler(key)

    def SetHandler(self, key, value):
        if key == "OnStackStart":
            self.stackModel.SetHandler("OnStackStart", value)
        else:
            super().SetHandler(key, value)

    def GetFrame(self):
        p = wx.Point(self.stackModel.GetProperty("position"))
        s = wx.Size(self.stackModel.GetProperty("size"))
        return wx.Rect(p, s)

    def GetDirty(self):
        if self.isDirty:
            return True
        for child in self.childModels:
            if child.isDirty:
                return True
        return False

    def SetDirty(self, isDirty):
        if isDirty:
            self.isDirty = True
        else:
            self.isDirty = False
            for child in self.childModels:
                child.isDirty = False

    def GetData(self):
        data = super().GetData()
        data["childModels"] = []
        for m in self.childModels:
            data["childModels"].append(m.GetData())
        data["properties"].pop("size")
        data["properties"].pop("position")
        return data

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            self.childModels.append(CardModel.ModelFromData(childData))

    def AddChild(self, model):
        self.childModels.append(model)
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        self.isDirty = True

    def GetDedupNameList(self, name, exclude):
        names = [m.properties["name"] for m in self.childModels]
        for n in exclude:
            if n in names:
                names.remove(n)
        return names

    def DeduplicateNameInCard(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(name, exclude)
        return super().DeduplicateName(name, names)

    def GetNextAvailableNameInCard(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(name, exclude)
        return super().GetNextAvailableName(name, names)

    def GetSize(self): return list(self.stackModel.GetProperty("size"))
    def SetSize(self, size): pass

    def GetBgColor(self): return self.GetProperty("bgColor")
    def SetBgColor(self, colorStr): self.SetProperty("bgColor", colorStr)

    @classmethod
    def ModelFromData(cls, data):
        m = None
        if data["type"] == "card":
            m = CardModel()
        elif data["type"] == "button":
            m = ButtonModel()
        elif data["type"] == "textfield":
            m = TextFieldModel()
        elif data["type"] == "textlabel":
            m = TextLabelModel()
        elif data["type"] == "image":
            m = ImageModel()
        elif data["type"] in ["pen", "line", "oval", "rect", "round_rect"]:
            m = UiShape.CreateModelForType(data["type"])
        m.SetData(data)
        return m
