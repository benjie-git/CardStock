#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel
import generator


class UiGroup(UiView):
    def __init__(self, parent, stackView, model):
        if not model.GetProperty("name"):
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("group_"), False)

        self.uiViews = []
        view = wx.Window(parent.view)
        view.SetBackgroundColour(None)

        super().__init__(parent, stackView, model, view)

    def GetCursor(self):
        if self.stackView.isEditing:
            return wx.CURSOR_HAND
        else:
            return None

    def SetModel(self, model):
        super().SetModel(model)
        self.RebuildViews()

    def GetAllUiViews(self):
        allUiViews = []
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                allUiViews.extend(uiView.GetAllUiViews())
        return allUiViews

    def OnResize(self, event):
        super().OnResize(event)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "child":
            self.RebuildViews()

    def RemoveChildViews(self):
        for ui in self.uiViews.copy():
            self.view.RemoveChild(ui.view)
            self.uiViews.remove(ui)

    def RebuildViews(self):
        for ui in self.uiViews.copy():
            self.view.RemoveChild(ui.view)
            self.uiViews.remove(ui)
        for m in self.model.childModels.copy():
            uiView = generator.StackGenerator.UiViewFromModel(self, self.stackView, m)
            self.uiViews.append(uiView)

    def OnIdle(self, event):
        if self.stackView.runner and "OnIdle" in self.model.handlers:
            self.stackView.runner.RunHandler(self.model, "OnIdle", event)
        for child in self.uiViews:
            child.OnIdle(event)


class GroupModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "group"

        self.childModels = []

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
        return data

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            model = generator.StackGenerator.ModelFromData(self.stackView, childData)
            model.parent = self
            self.childModels.append(model)

    def AddChildModels(self, models):
        selfPos = self.GetProperty("position")
        for model in models.copy():
            self.childModels.append(model)
            model.parent = self
            pos = model.GetProperty("position")
            model.SetProperty("position", [pos[0]-selfPos[0], pos[1]-selfPos[1]], False)
        self.UpdateFrame()
        self.Notify("child")
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        model.parent = None
        pos = model.GetProperty("position")
        selfPos = self.GetProperty("position")
        model.SetProperty("position", [pos[0]+selfPos[0], pos[1]+selfPos[1]], False)
        self.isDirty = True

    def UpdateFrame(self):
        if len(self.childModels):
            oldRect = self.GetFrame()
            newRect = self.childModels[0].GetFrame()
            for m in self.childModels[1:]:
                newRect = newRect.Union(m.GetFrame())
            newRect = wx.Rect(wx.Point(oldRect.Position.x + newRect.Position.x,
                                              oldRect.Position.y + newRect.Position.y), newRect.Size)
            self.SetFrame(newRect)
            offset = (newRect.Left - oldRect.Left, newRect.Top - oldRect.Top)
            for m in self.childModels:
                oldPos = m.GetProperty("position")
                m.SetProperty("position", [oldPos[0] - offset[0], oldPos[1] - offset[1]], False)
