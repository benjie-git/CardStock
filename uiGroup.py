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
        view = wx.Window(parent.view, style=wx.TRANSPARENT_WINDOW)
        view.Bind(wx.EVT_PAINT, self.OnPaintGroup)
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
        self.model.ResizeChildModels()
        self.view.Refresh()
        self.view.Update()

    def OnPaintGroup(self, event):
        dc = wx.PaintDC(self.view)
        dc.SetPen(wx.Pen('Gray', 1, wx.PENSTYLE_DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle((1, 1), (self.view.GetSize()[0]-1, self.view.GetSize()[1]-1))
        event.Skip()


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
        self.origFrame = None

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

    def SetFromModel(self, model):
        super().SetFromModel(model)
        self.origFrame = self.GetFrame()
        for model in model.childModels:
            model.origGroupSubviewFrame = model.GetFrame()

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            model = generator.StackGenerator.ModelFromData(self.stackView, childData)
            model.parent = self
            self.childModels.append(model)
            model.origGroupSubviewFrame = model.GetFrame()
        self.origFrame = self.GetFrame()

    def AddChildModels(self, models):
        selfPos = self.GetProperty("position")
        for model in models:
            self.childModels.append(model)
            model.parent = self
            pos = model.GetProperty("position")
            model.SetProperty("position", [pos[0]-selfPos[0], pos[1]-selfPos[1]], False)
        self.UpdateFrame()
        self.origFrame = self.GetFrame()
        for model in models:
            model.origGroupSubviewFrame = model.GetFrame()
        self.Notify("child")
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        model.parent = None
        model.origGroupSubviewFrame = None
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

    def ResizeChildModels(self):
        scaleX = 1
        scaleY = 1
        if self.origFrame.Size.Width != 0:
            scaleX = self.GetFrame().Size.Width / self.origFrame.Size.Width
        if self.origFrame.Size.Height != 0:
            scaleY = self.GetFrame().Size.Height / self.origFrame.Size.Height
        for m in self.childModels:
            pos = m.origGroupSubviewFrame.Position
            size = m.origGroupSubviewFrame.Size

            pos = wx.Point(pos.x * scaleX, pos.y * scaleY)
            size = wx.Size(size.Width * scaleX, size.Height * scaleY)
            m.SetFrame(wx.Rect(pos, size))
