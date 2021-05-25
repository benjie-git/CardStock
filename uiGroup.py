import wx
from uiView import *
import generator
from codeRunnerThread import RunOnMainSync


class UiGroup(UiView):
    """
    This class is a controller that coordinates management of a group view, based on data from a GroupModel.
    A group does not use its own wx.Window as a view, but instead draws itself onto the stack view.
    Many of a group's methods just pass along messages to all of its children.
    """

    def __init__(self, parent, stackManager, model):
        self.uiViews = []
        super().__init__(parent, stackManager, model, None)

    def SetDown(self):
        for ui in self.uiViews:
            ui.SetDown()
        self.uiViews = None
        super().SetDown()

    def SetModel(self, model):
        super().SetModel(model)
        self.RebuildViews()

    def GetAllUiViews(self, allUiViews):
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)

    def HitTest(self, pt):
        if not self.hitRegion:
            self.MakeHitRegion()
        if self.hitRegion.Contains(pt):
            for ui in reversed(self.uiViews):
                if not ui.model.IsHidden():
                    hit = ui.HitTest(pt-wx.Point(ui.model.GetProperty("position")))
                    if hit:
                        return hit
            return self
        return None

    def MakeHitRegion(self):
        if self.stackManager.isEditing:
            # The group's whole rect is a click target while editing
            super().MakeHitRegion()
        else:
            if self.model.IsHidden():
                self.hitRegion = wx.Region((0, 0), (0, 0))

            # Only the sub-objects are click targets while running
            reg = wx.Region()
            for ui in self.uiViews:
                uiReg = wx.Region(ui.GetHitRegion())
                uiReg.Offset(wx.Point(ui.model.GetProperty("position")))
                reg.Union(uiReg)
            self.hitRegion = reg

    def Paint(self, gc):
        if self.stackManager.isEditing:
            gc.SetPen(wx.Pen('Gray', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.model.GetAbsoluteFrame())

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "position":
            for ui in self.uiViews:
                ui.OnPropertyChanged(ui.model, key)
        elif key == "size":
            self.model.ResizeChildModels()
        elif key == "child":
            self.RebuildViews()
            self.stackManager.view.Refresh()

    def RemoveChildViews(self):
        for ui in self.uiViews.copy():
            if ui.view:
                self.stackManager.view.RemoveChild(ui.view)
                ui.view.Destroy()
            if ui.model.type == "group":
                ui.RemoveChildViews()
            self.uiViews.remove(ui)

    def RebuildViews(self):
        for ui in self.uiViews.copy():
            if ui.view:
                self.stackManager.view.RemoveChild(ui.view)
                wx.CallAfter(ui.view.Destroy)
            self.uiViews.remove(ui)
        for m in self.model.childModels.copy():
            uiView = generator.StackGenerator.UiViewFromModel(self, self.stackManager, m)
            self.uiViews.append(uiView)

    def OnPeriodic(self, event):
        didRun = False
        if super().OnPeriodic(event):
            didRun = True
        for child in self.uiViews:
            if child.OnPeriodic(event):
                didRun = True
        return didRun


class GroupModel(ViewModel):
    """
    Model for a Group object.  Mostly forwards messages to all of its children.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "group"
        self.origFrame = None
        self.proxyClass = Group
        self.properties["name"] = "group_1"

    def GetAllChildModels(self):
        allModels = []
        for child in self.childModels:
            allModels.append(child)
            if child.type == "group":
                allModels.extend(child.GetAllChildModels())
        return allModels

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
            model = generator.StackGenerator.ModelFromData(self.stackManager, childData)
            model.parent = self
            self.childModels.append(model)
            model.origGroupSubviewFrame = model.GetFrame()
        self.origFrame = self.GetFrame()

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        super().SetProperty(key, value, notify)
        if key == "hidden":
            for m in self.GetAllChildModels():
                m.Notify("hidden")

    def AddChildModels(self, models):
        selfPos = self.GetProperty("position")
        for model in models:
            self.childModels.append(model)
            model.parent = self
            pos = model.GetProperty("position")
            model.SetProperty("position", [pos[0]-selfPos[0], pos[1]-selfPos[1]], notify=False)
        self.UpdateFrame()
        self.origFrame = self.GetFrame()
        for model in models:
            model.origGroupSubviewFrame = model.GetFrame()
        self.Notify("child")
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        model.origGroupSubviewFrame = None
        pos = model.GetProperty("position")
        selfPos = self.GetProperty("position")
        model.SetProperty("position", [pos[0]+selfPos[0], pos[1]+selfPos[1]], notify=False)
        model.SetDown()
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
                m.SetProperty("position", [oldPos[0] - offset[0], oldPos[1] - offset[1]], notify=False)

    def PerformFlips(self, fx, fy, notify=True):
        if fx or fy:
            for m in self.childModels:
                pos = m.origGroupSubviewFrame.Position
                size = m.origGroupSubviewFrame.Size
                pos = wx.Point((self.origFrame.Size.width - (pos.x + size.width)) if fx else pos.x,
                               (self.origFrame.Size.height - (pos.y + size.height)) if fy else pos.y)
                m.origGroupSubviewFrame.Position = pos
            for m in self.childModels:
                m.PerformFlips(fx, fy, notify=notify)
            self.ResizeChildModels()
        if notify:
            self.Notify("size")

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


class Group(ViewProxy):
    """
    Group proxy objects are the user-accessible objects exposed to event handler code for group objects.
    """

    @RunOnMainSync
    def Ungroup(self):
        model = self._model
        if not model: return None
        groups = model.stackManager.UngroupModelsInternal([model])
        if groups and len(groups) > 0:
            return groups[0]

    def StopAllAnimating(self, propertyName=None):
        model = self._model
        if not model: return
        model.StopAnimation(propertyName)
        for child in model.GetAllChildModels():
            child.StopAnimation(propertyName)
