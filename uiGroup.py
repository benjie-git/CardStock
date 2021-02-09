#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import *
import generator


class UiGroup(UiView):
    def __init__(self, parent, stackView, model):
        if not model.GetProperty("name"):
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("group_"), False)

        self.uiViews = []

        super().__init__(parent, stackView, model, None)

    def GetCursor(self):
        if self.stackView.isEditing:
            return wx.CURSOR_HAND
        else:
            return None

    def SetModel(self, model):
        super().SetModel(model)
        self.RebuildViews()

    def DestroyView(self):
        for uiView in self.uiViews:
            uiView.DestroyView()

    def ReparentView(self, newParent):
        for uiView in self.uiViews:
            uiView.ReparentView(newParent)

    def GetAllUiViews(self):
        allUiViews = []
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                allUiViews.extend(uiView.GetAllUiViews())
        return allUiViews

    def HitTest(self, pt):
        if not self.hitRegion:
            self.MakeHitRegion()
        if self.hitRegion.Contains(pt):
            for ui in reversed(self.uiViews):
                hit = ui.HitTest(pt-wx.Point(ui.model.GetProperty("position")))
                if hit:
                    return hit
            return self
        return None

    def Paint(self, gc):
        if self.stackView.isEditing:
            gc.SetPen(wx.Pen('Gray', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.model.GetAbsoluteFrame())
        for uiView in self.uiViews:
            uiView.Paint(gc)

    def PaintSelectionBox(self, gc):
        super().PaintSelectionBox(gc)
        for uiView in self.uiViews:
            uiView.PaintSelectionBox(gc)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "position":
            for ui in self.uiViews:
                ui.OnPropertyChanged(ui.model, key)
        elif key == "size":
            self.model.ResizeChildModels()
        elif key == "child":
            self.RebuildViews()

    def RemoveChildViews(self):
        for ui in self.uiViews.copy():
            if ui.view:
                self.stackView.RemoveChild(ui.view)
                ui.view.Destroy()
            if ui.model.type == "group":
                ui.RemoveChildViews()
            self.uiViews.remove(ui)

    def RebuildViews(self):
        for ui in self.uiViews.copy():
            if ui.view:
                self.stackView.RemoveChild(ui.view)
                ui.view.Destroy()
            self.uiViews.remove(ui)
        for m in self.model.childModels.copy():
            uiView = generator.StackGenerator.UiViewFromModel(self, self.stackView, m)
            self.uiViews.append(uiView)

    def OnIdle(self, event):
        super().OnIdle(event)
        for child in self.uiViews:
            child.OnIdle(event)


class GroupModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "group"
        self.origFrame = None

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
