# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
        super().__init__(parent, stackManager, model, None)

    def SetModel(self, model):
        super().SetModel(model)
        self.RebuildViews()

    def GetAllUiViews(self, allUiViews):
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)

    def HitTest(self, pt):
        f = self.model.GetAbsoluteFrame()
        f.Inflate(20)
        if f.Contains(pt):
            if not self.hitRegion:
                self.MakeHitRegion()
            if self.hitRegion.Contains(pt):
                for ui in reversed(self.uiViews):
                    if ui.model.IsVisible():
                        hit = ui.HitTest(pt)
                        if hit:
                            return hit
                return self
        return None

    def ClearHitRegion(self, noParent=False):
        super().ClearHitRegion(noParent)
        for ui in self.uiViews:
            ui.ClearHitRegion(noParent=True)

    def MakeHitRegion(self):
        # Make a region in abs/card coordinates
        if self.stackManager.isEditing:
            # The group's whole rect is a click target while editing
            super().MakeHitRegion()
        else:
            if not self.model.IsVisible():
                self.hitRegion = wx.Region((0, 0), (0, 0))

            # Only the sub-objects are click targets while running
            reg = wx.Region()
            for ui in self.uiViews:
                uiReg = wx.Region(ui.GetHitRegion())
                reg.Union(uiReg)
            self.hitRegion = reg
            self.hitRegionOffset = self.model.GetAbsolutePosition()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["position", "rotation"]:
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
        self.properties["rotation"] = 0.0
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "position", "size", "rotation"]

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
            model.origGroupSubviewRotation = model.GetProperty("rotation")

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            model = generator.StackGenerator.ModelFromData(self.stackManager, childData)
            model.parent = self
            self.childModels.append(model)
            model.origGroupSubviewFrame = model.GetFrame()
            model.origGroupSubviewRotation = model.GetProperty("rotation")
        self.origFrame = self.GetFrame()

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        super().SetProperty(key, value, notify)
        if key == "is_visible":
            for m in self.GetAllChildModels():
                m.Notify("is_visible")

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
            model.origGroupSubviewRotation = model.GetProperty("rotation")
        self.Notify("child")
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        del model.origGroupSubviewFrame
        del model.origGroupSubviewRotation
        pos = model.GetProperty("position")
        selfPos = self.GetProperty("position")
        model.SetProperty("position", [pos[0]+selfPos[0], pos[1]+selfPos[1]], notify=False)
        model.SetDown()
        self.isDirty = True

    def UpdateFrame(self):
        if len(self.childModels):
            oldRect = self.GetFrame()
            newRect = self.childModels[0].GetAbsoluteFrame()
            for m in self.childModels[1:]:
                newRect = newRect.Union(m.GetAbsoluteFrame())
            self.SetFrame(newRect)
            offset = (newRect.Left - oldRect.Left, newRect.Top - oldRect.Top)
            for m in self.childModels:
                oldPos = m.GetProperty("position")
                m.SetProperty("position", [oldPos[0] - offset[0], oldPos[1] - offset[1]], notify=False)

    def PerformFlips(self, fx, fy, notify=True):
        super().PerformFlips(fx, fy, notify)
        if fx or fy:
            for m in self.childModels:
                if fx != fy:
                    if m.origGroupSubviewRotation is None:
                        m.origGroupSubviewRotation = 0
                    m.origGroupSubviewRotation = -m.origGroupSubviewRotation
                pos = m.origGroupSubviewFrame.Position
                size = m.origGroupSubviewFrame.Size
                pos = wx.Point((self.origFrame.Size.width - (pos.x + size.width)) if fx else pos.x,
                               (self.origFrame.Size.height - (pos.y + size.height)) if fy else pos.y)
                m.origGroupSubviewFrame.Position = pos
            for m in self.childModels:
                m.PerformFlips(fx, fy, notify=notify)
                if fx != fy:
                    rot = m.GetProperty("rotation")
                    if rot is not None:
                        m.SetProperty("rotation", -rot)
            self.ResizeChildModels()
        if notify:
            self.Notify("size")

    def ResizeChildModels(self):
        scaleX = 1
        scaleY = 1
        f = self.GetFrame()
        if self.origFrame.Size.Width != 0:
            scaleX = f.Size.Width / self.origFrame.Size.Width
        if self.origFrame.Size.Height != 0:
            scaleY = f.Size.Height / self.origFrame.Size.Height
        for m in self.childModels:
            pos = m.origGroupSubviewFrame.Position
            size = m.origGroupSubviewFrame.Size
            oldRot = m.origGroupSubviewRotation
            if oldRot is None:
                oldRot = 0
            if oldRot == 0:
                # If this child is not rotated, just scale it
                m.SetFrame(wx.Rect((int(pos.x*scaleX), int(pos.y*scaleY)), (int(size.Width*scaleX), int(size.Height*scaleY))))
            else:
                # If this child is rotated, we need to scale its size, but also scale the rotation
                pos = (pos.x*scaleX, pos.y*scaleY)

                # Set up the transform to get the rotated corner points
                aff = wx.AffineMatrix2D()
                aff.Translate(int(size[0] / 2), int(size[1] / 2))
                aff.Rotate(math.radians(-oldRot))
                aff.Translate(-int(size[0] / 2), -int(size[1] / 2))

                # Get rotated corner points
                rect = wx.Rect((0, 0), size)
                points = m.RotatedRectPoints(rect, aff)
                points = [wx.RealPoint(p[0]*scaleX, p[1]*scaleY)+pos for p in points]

                # Get the slopes of both pairs of parallel sides of the parallelogram
                # And use the slope of the longer sides
                diff = points[2]-points[1]
                rotA = math.degrees(math.atan2(diff.x, diff.y))
                diff = points[0]-points[1]
                rotB = 90+math.degrees(math.atan2(diff.x, diff.y))
                if size.Height < size.Width:
                    rot = rotB
                else:
                    rot = rotA
                m.SetProperty("rotation", rot)

                # Find the center and the size of the new scaled state for this shape
                center = wx.Point(int((points[0].x + points[1].x + points[2].x + points[3].x) / 4),
                                  int((points[0].y + points[1].y + points[2].y + points[3].y) / 4))
                if size.Height > size.Width:
                    # if the height is longer, scale the width to get thinner as the parallelogram folds up
                    size = wx.Size(int(math.cos(math.radians(rotB-rotA)) * math.sqrt((points[0].x - points[1].x)**2 + (points[0].y - points[1].y)**2)),
                                   int(math.sqrt((points[1].x - points[2].x) ** 2 + (points[1].y - points[2].y) ** 2)))
                else:
                    # if the width is longer, scale the height to get thinner as the parallelogram folds up
                    size = wx.Size(int(math.sqrt((points[0].x - points[1].x) ** 2 + (points[0].y - points[1].y) ** 2)),
                                   int(math.cos(math.radians(rotB-rotA)) * math.sqrt((points[1].x - points[2].x) ** 2 + (points[1].y - points[2].y) ** 2)))
                m.SetFrame(wx.Rect(tuple(int(x) for x in (center - tuple(size/2))), size))


class Group(ViewProxy):
    """
    Group proxy objects are the user-accessible objects exposed to event handler code for group objects.
    """

    @RunOnMainSync
    def ungroup(self):
        model = self._model
        if not model: return None
        groups = model.stackManager.UngroupModelsInternal([model])
        if groups and len(groups) > 0:
            return groups[0]

    def stop_all_animating(self, property_name=None):
        model = self._model
        if not model: return
        model.StopAnimation(property_name)
        for child in model.GetAllChildModels():
            child.StopAnimation(property_name)
