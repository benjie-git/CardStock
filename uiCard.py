#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *
import generator


class UiCard(UiView):
    def __init__(self, parent, stackView, model):
        if not model.GetProperty("name"):
            model.SetProperty("name", model.GetNextAvailableNameInCard("card_"), False)

        super().__init__(parent, stackView, model, stackView)
        self.stackView.stackModel.SetProperty("size", self.view.GetSize(), False)
        self.view.SetBackgroundColour(self.model.GetProperty("bgColor"))

    def SetView(self, view):
        super().SetView(view)
        self.model.SetProperty("size", self.view.GetSize(), False)
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
        if self.stackView.runner and self.model.GetHandler("OnKeyDown"):
            self.stackView.runner.RunHandler(self.model, "OnKeyDown", event)

    def OnKeyUp(self, event):
        if self.stackView.runner and self.model.GetHandler("OnKeyUp"):
            self.stackView.runner.RunHandler(self.model, "OnKeyUp", event)

    def OnIdle(self, event):
        super().OnIdle(event)
        for child in self.stackView.uiViews:
            child.OnIdle(event)


class CardModel(ViewModel):
    minSize = wx.Size(200, 200)

    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "card"
        self.stackModel = None  # For setting stack size
        self.proxyClass = CardProxy
        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "", "OnShowCard": "", "OnHideCard": "", "OnKeyDown": "", "OnKeyUp": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        # Custom property order and mask for the inspector
        self.properties["bgColor"] = "white"
        self.propertyKeys = ["name", "bgColor", "size"]
        self.propertyTypes["bgColor"] = "color"

    def SetProperty(self, key, value, notify=True):
        if key == "size":
            self.stackModel.SetProperty("size", value, notify)
        else:
            super().SetProperty(key, value, notify)

    def GetProperty(self, key):
        if key == "size":
            return self.stackModel.GetProperty("size")
        else:
            return super().GetProperty(key)

    def GetFrame(self):
        s = self.stackModel.GetProperty("size")
        return wx.Rect((0,0), s)

    def GetAbsoluteFrame(self):
        return self.GetFrame()

    def GetAllChildModels(self):
        allModels = []
        for child in self.childModels:
            allModels.append(child)
            if child.type == "group":
                allModels.extend(child.GetAllChildModels())
        return allModels

    def GetDirty(self):
        if self.isDirty:
            return True
        for child in self.GetAllChildModels():
            if child.isDirty:
                return True
        return False

    def SetDirty(self, isDirty):
        if isDirty:
            self.isDirty = True
        else:
            self.isDirty = False
            for child in self.GetAllChildModels():
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
            self.childModels.append(generator.StackGenerator.ModelFromData(self.stackView, childData))

    def AddChild(self, model):
        self.childModels.append(model)
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        self.isDirty = True

    def GetDedupNameList(self, name, exclude):
        names = [m.properties["name"] for m in self.GetAllChildModels()]
        for n in exclude:
            if n in names:
                names.remove(n)
        return names

    def DeduplicateNameInCard(self, name, exclude=None, include=None):
        if exclude is None: exclude = []
        if include is None: include = []
        names = self.GetDedupNameList(name, exclude)
        names.extend(include)
        return super().DeduplicateName(name, names)

    def GetNextAvailableNameInCard(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(name, exclude)
        return super().GetNextAvailableName(name, names)


class CardProxy(ViewProxy):
    @property
    def bgColor(self):
        return self._model.GetProperty("bgColor")
    @bgColor.setter
    def bgColor(self, val):
        self._model.SetProperty("bgColor", val)

    @property
    def index(self):
        return self._model.stackModel.childModels.index(self._model)
