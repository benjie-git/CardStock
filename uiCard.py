#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel
from uiButton import ButtonModel
from uiTextField import TextFieldModel
from uiTextLabel import TextLabelModel
from uiImage import ImageModel


class UiCard(UiView):
    def __init__(self, stackView, model):
        if not model.GetProperty("name"):
            model.SetProperty("name", model.GetNextAvailableNameForBase("card_"))

        super().__init__(stackView, model, stackView)
        self.model.SetProperty("size", self.view.GetSize())

    def SetView(self, view):
        super().SetView(view)
        self.model.SetProperty("size", self.view.GetSize())

    def OnResize(self, event):
        super().OnResize(event)
        self.model.SetProperty("size", self.view.GetSize())

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "name":
            self.stackView.designer.UpdateCardList()

    def OnKeyDown(self, event):
        if not self.stackView.isEditing:
            if self.model.runner and "OnKeyDown" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnKeyDown", event)
        else:
            event.Skip()

    def OnKeyUp(self, event):
        if not self.stackView.isEditing:
            if self.model.runner and "OnKeyUp" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnKeyUp", event)

    def OnIdle(self, event):
        if not self.stackView.isEditing:
            if self.model.runner and "OnIdle" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnIdle", event)
            for m in self.model.childModels:
                if m.runner and "OnIdle" in m.handlers:
                    m.runner.RunHandler(m, "OnIdle", event)


class CardModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "card"

        # Add custom handlers to the top of the list
        handlers = {"OnStart": "", "OnShowCard": "", "OnHideCard": "","OnIdle": "", "OnKeyDown": "", "OnKeyUp": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "size"]

        self.childModels = []
        self.shapes = []

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
        data["shapes"] = self.shapes
        data["childModels"] = []
        for m in self.childModels:
            data["childModels"].append(m.GetData())
        return data

    def SetData(self, data):
        super().SetData(data)
        self.shapes = data["shapes"]
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

    def DeduplicateName(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(name, exclude)
        return super().DeduplicateNameInternal(name, names)

    def GetNextAvailableNameForBase(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(name, exclude)
        return super().GetNextAvailableNameForBaseInternal(name, names)

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
        m.SetData(data)
        return m
