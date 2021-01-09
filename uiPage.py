#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from uiView import UiView, ViewModel
from uiButton import ButtonModel
from uiTextField import TextFieldModel
from uiTextLabel import TextLabelModel
from uiImage import ImageModel


class UiPage(UiView):
    def __init__(self, page, model=None):
        if not model:
            model = PageModel()
        if not model.GetProperty("name"):
            model.SetProperty("name", model.GetNextAvailableNameForBase("page_"))

        super().__init__(page, model, page)
        self.model.SetProperty("size", self.view.GetSize())

    def SetView(self, view):
        super().SetView(view)
        view.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        view.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.model.SetProperty("size", self.view.GetSize())

    def OnResize(self, event):
        super().OnResize(event)
        self.model.SetProperty("size", self.view.GetSize())

    def OnKeyDown(self, event):
        if not self.isEditing:
            if "OnKeyDown" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnKeyDown", event)
        else:
            event.Skip()

    def OnKeyUp(self, event):
        if not self.isEditing:
            if "OnKeyUp" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnKeyUp", event)

    def OnIdle(self, event):
        if not self.isEditing:
            if "OnIdle" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnIdle", event)
            event.Skip()


class PageModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "page"

        # Add custom handlers to the top of the list
        handlers = {"OnStart": "", "OnIdle": "", "OnKeyDown": "", "OnKeyUp": ""}
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
            self.childModels.append(PageModel.ModelFromData(childData))

    def AddChild(self, model):
        self.childModels.append(model)
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        self.isDirty = True

    def DeduplicateName(self, name, exclude=[]):
        names = [m.properties["name"] for m in self.childModels]
        names.extend(["page", "self"])
        for n in exclude:
            if n in names:
                names.remove(n)

        if name in names:
            name = name.rstrip("0123456789")
            if name[-1:] != "_":
                name = name + "_"
            name = self.GetNextAvailableNameForBase(name, exclude)
        return name

    def GetNextAvailableNameForBase(self, base, exclude=[]):
        names = [m.GetProperty("name") for m in self.childModels]
        for n in exclude:
            if n in names:
                names.remove(n)
        i = 0
        while True:
            i += 1
            name = base+str(i)
            if name not in names:
                return name

    @classmethod
    def ModelFromData(cls, data):
        m = None
        if data["type"] == "page":
            m = PageModel()
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
