# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from uiView import *
import uiShape
import generator
from codeRunnerThread import RunOnMainSync, RunOnMainAsync


class UiCard(UiView):
    """
    This class is a controller that coordinates management of the stack view while this card is shown,
    based on data from a CardModel.
    The UiCard.view is the same wx.Window as the stackManager.view.
    There is only ever one UiCard, and it gets its model replaced with another CardModel when switching cards.
    """

    def __init__(self, parent, stackManager, model):
        self.runningInternalResize = False
        super().__init__(parent, stackManager, model, stackManager.view)

    def DestroyView(self):
        if self.view:
            if self.view.HasCapture():
                self.view.ReleaseMouse()
            self.view = None

    def RemoveUiViews(self):
        for ui in self.uiViews.copy():
            if ui.model.type != "card":
                self.uiViews.remove(ui)
            ui.SetDown()

    def GetAllUiViews(self):
        allUiViews = []
        for uiView in self.uiViews:
            allUiViews.append(uiView)
            if uiView.model.type == "group":
                uiView.GetAllUiViews(allUiViews)
        return allUiViews

    def SetModel(self, model):
        super().SetModel(model)
        self.RemoveUiViews()

    def GetCursor(self):
        return None

    def ResizeCardView(self, newModelSize):
        size = self.view.FromDIP(newModelSize)
        self.runningInternalResize = True
        self.view.SetSize(size)
        self.view.SetPosition((0,0))
        self.runningInternalResize = False

    def OnResize(self, event):
        didEnqueue = False
        self.stackManager.view.didResize = True
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetProperty("can_resize"):
            didEnqueue = self.stackManager.runner.RunHandler(self.model, "on_resize", None, False)
        if self.stackManager.isEditing or not didEnqueue:
            self.stackManager.view.Refresh()
            self.stackManager.view.RefreshIfNeeded()
        event.Skip()

    def Paint(self, gc):
        bg = wx.Colour(self.model.GetProperty("fill_color"))
        if not bg:
            bg = wx.Colour('white')
        gc.SetBrush(wx.Brush(bg, wx.BRUSHSTYLE_SOLID))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(self.model.GetFrame().Inflate(1))

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()
            f.Top += 1
            gc.SetPen(wx.Pen('Blue', self.stackManager.view.FromDIP(3), wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Deflate(self.stackManager.view.FromDIP(1)))

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            for box in self.GetLocalResizeBoxRects().values():
                r = wx.Rect(box.TopLeft + f.TopLeft, box.Size)
                gc.DrawRectangle(r)

    def GetLocalResizeBoxPoints(self):
        # the resize box/handle should hang out of the frame, to allow grabbing it from behind
        # native widgets which can obscure the full frame.
        # Return as a dict, so each point is labelled
        s = self.model.GetProperty("size")
        return {"BR":wx.Point(s.width-7,6)}

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "name":
            self.stackManager.designer.UpdateCardList()
        elif key == "fill_color":
            self.view.Refresh()
        elif key == "size":
            if self == self.stackManager.uiCard and self.stackManager.runner and self.stackManager.runner.viewer:
                self.stackManager.runner.viewer.SetupViewerSize()
            for ui in self.uiViews:
                ui.ClearHitRegion()
                ui.OnPropertyChanged(ui.model, "position")

    def OnKeyDown(self, event):
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_key_press"):
            self.stackManager.runner.RunHandler(self.model, "on_key_press", event)

    def OnKeyUp(self, event):
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_key_release"):
            self.stackManager.runner.RunHandler(self.model, "on_key_release", event)

    def OnPeriodic(self, event):
        didRun = False
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_key_hold"):
            for key_name in self.stackManager.runner.pressedKeys:
                self.stackManager.runner.RunHandler(self.model, "on_key_hold", event, key_name)
                didRun = True
        for child in reversed(self.GetAllUiViews()):
            if child.OnPeriodic(event):
                didRun = True
        if super().OnPeriodic(event):
            didRun = True
        return didRun


class CardModel(ViewModel):
    """
    The CardModel allows access to a few properties that actually live in the stack.  This is because the Designer
    allows editing cards, but not the stack model itself.  These properties are size, can_save, and can_resize.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "card"
        self.proxyClass = Card
        # Add custom handlers to the top of the list
        handlers = {"on_setup": "", "on_show_card": "", "on_key_press": "", "on_key_hold": "", "on_key_release": ""}
        del self.handlers["on_bounce"]
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.handlers["on_resize"] = ""
        self.handlers["on_hide_card"] = ""
        self.initialEditHandler = "on_setup"

        # Custom property order and mask for the inspector
        self.properties["name"] = "card_1"
        self.properties["fill_color"] = "white"
        self.properties["size"] = wx.Size(500, 500)
        self.properties["can_resize"] = False
        self.propertyKeys = ["name", "fill_color", "size", "can_resize"]

        self.propertyTypes["fill_color"] = "color"
        self.propertyTypes["can_resize"] = 'bool'

    def GetAbsoluteFrame(self):
        return self.GetFrame()

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
        data["properties"].pop("position")
        return data

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            m = generator.StackGenerator.ModelFromData(self.stackManager, childData)
            m.parent = self
            self.childModels.append(m)

    def AddChild(self, model):
        self.InsertChild(model, len(self.childModels))

    def InsertChild(self, model, index):
        self.childModels.insert(index, model)
        model.parent = self
        self.isDirty = True
        if not self.stackManager.isEditing and self.stackManager.runner and self.stackManager.uiCard.model == self:
            self.stackManager.runner.SetupForCard(self)

    def RemoveChild(self, model):
        self.childModels.remove(model)
        model.SetDown()
        self.isDirty = True
        if not self.stackManager.isEditing and self.stackManager.runner and self.stackManager.uiCard.model == self:
            self.stackManager.runner.SetupForCard(self)

    def AddNewObject(self, typeStr, name, size, points=None, kwargs=None):
        if not isinstance(name, str):
            raise TypeError("name is not a string")

        # immediately create the new object and add it to the card model
        model = generator.StackGenerator.ModelFromType(self.stackManager, typeStr)
        model.SetProperty("name", name, notify=False)
        self.DeduplicateNamesForModels([model])
        if size:
            model.SetProperty("size", size, notify=False)
        if isinstance(model, uiShape.LineModel):
            model.type = typeStr
            if points:
                model.points = points
                model.ReCropShape()

        if kwargs:
            if "center" in kwargs and "size" in kwargs:
                model.SetProperty("size", kwargs["size"], notify=False)
                model.SetProperty("center", kwargs["center"], notify=False)
                kwargs.pop("size")
                kwargs.pop("center")

            for k,v in kwargs.items():
                if hasattr(model.GetProxy(), k):
                    setattr(model.GetProxy(), k, v)
                else:
                    raise TypeError(f"unable to set property {k}")

        self.AddChild(model)

        @RunOnMainAsync
        def func():
            # add the view on the main thread
            if self.didSetDown: return
            if self.stackManager.uiCard.model == self:
                self.stackManager.AddUiViewsFromModels([model], canUndo=False)
            self.stackManager.view.Refresh()
        func()

        return model

    def PerformFlips(self, fx, fy, notify=True):
        super().PerformFlips(fx, fy, notify)
        cardSize = self.GetProperty("size")
        if fx or fy:
            for m in self.childModels:
                m.PerformFlips(fx, fy, notify=notify)
            for m in self.childModels:
                pos = m.GetProperty("position")
                size = m.GetProperty("size")
                pos = wx.Point(int((cardSize.width - (pos.x + size.width)) if fx else pos.x),
                               int((cardSize.height - (pos.y + size.height)) if fy else pos.y))
                m.SetProperty("position", pos, notify=notify)
        if notify:
            self.Notify("size")

    def broadcast_message(self, message):
        def r_broadcast(model):
            self.stackManager.runner.RunHandler(model, "on_message", None, message)
            for m in model.childModels:
                r_broadcast(m)
        r_broadcast(self)

    def GetDedupNameList(self, exclude):
        names = [m.properties["name"] for m in self.GetAllChildModels()]
        for n in exclude:
            if n in names:
                names.remove(n)
        return names

    def DeduplicateNameInCard(self, name, exclude=None, include=None):
        if exclude is None: exclude = []
        if include is None: include = []
        names = self.GetDedupNameList(exclude)
        names.extend(include)
        return super().DeduplicateName(name, names)

    def GetNextAvailableNameInCard(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(exclude)
        return super().GetNextAvailableName(name, names)

    def DeduplicateNamesForModels(self, models):
        usedNames = []

        def dedup(obj):
            c = obj.GetCard()
            if not c or c != self:
                newName = self.DeduplicateNameInCard(obj.GetProperty("name"), None, usedNames)
                obj.SetProperty("name", newName)
                usedNames.append(newName)
                for m in obj.childModels:
                    dedup(m)

        for m in models:
            dedup(m)



class Card(ViewProxy):
    """
    Card proxy objects are the user-accessible objects exposed to event handler code for card objects.
    """

    @property
    def fill_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fill_color")
    @fill_color.setter
    def fill_color(self, val):
        if not isinstance(val, str):
            raise TypeError("fill_color must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fill_color", val)

    @property
    def number(self):
        model = self._model
        if not model: return -1
        return model.parent.childModels.index(model)+1

    def broadcast_message(self, message):
        if not self._model: return
        if not isinstance(message, str):
            raise TypeError("broadcast_message(): message must be a string")
        self._model.broadcast_message(message)

    def animate_fill_color(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_fill_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_fill_color(): end_color must be a string")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_fill_color(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        end_color = wx.Colour(endVal)
        if end_color.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.fill_color)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("fill_color", wx.Colour([int(animDict["origParts"][i] + animDict["offsets"][i] * ease(progress, easing)) for i in range(4)]))

            def internalOnFinished(animDict):
                if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

            model.AddAnimation("fill_color", duration, onUpdate, onStart, internalOnFinished)

    def add_button(self, name="button", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("button", name, (100,24), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_text_field(self, name="field", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("textfield", name, (100,24), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_text_label(self, name="label", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("textlabel", name, (100,24), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_image(self, name="image", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("image", name, (80,80), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_oval(self, name="oval", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("oval", name, None, [(10, 10), (100, 100)], kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_rectangle(self, name="rect", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("rect", name, None, [(10, 10), (100, 100)], kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_round_rectangle(self, name="roundrect", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("roundrect", name, None, [(10, 10), (100, 100)], kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def add_line(self, points, name="line", **kwargs):
        if not isinstance(points, (list, tuple)):
            raise TypeError("add_line(): points should be a list of points")
        if len(points) < 2:
            raise TypeError("add_line(): points should be a list of at least 2 points")
        for p in points:
            if not isinstance(p, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
                raise TypeError("add_line(): points items each need to be a point or a list of two numbers")
            if len(p) != 2:
                raise TypeError("add_line(): points items each need to be a point or a list of two numbers")
            try:
                int(p[0]), int(p[1])
            except:
                raise ValueError("add_line(): points items each need to be a point or a list of two numbers")

        model = self._model
        if not model: return None

        line = model.AddNewObject("line", name, None, points, kwargs=kwargs)
        return line.GetProxy() if line else None

    def add_polygon(self, points, name="polygon", **kwargs):
        if not isinstance(points, (list, tuple)):
            raise TypeError("add_polygon(): points should be a list of points")
        if len(points) < 2:
            raise TypeError("add_polygon(): points should be a list of at least 2 points")
        for p in points:
            if not isinstance(p, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
                raise TypeError("add_polygon(): points items each need to be a point or a list of two numbers")
            if len(p) != 2:
                raise TypeError("add_polygon(): points items each need to be a point or a list of two numbers")
            try:
                int(p[0]), int(p[1])
            except:
                raise ValueError("add_polygon(): points items each need to be a point or a list of two numbers")

        model = self._model
        if not model: return None

        poly = model.AddNewObject("polygon", name, None, points, kwargs=kwargs)
        return poly.GetProxy() if poly else None

    def add_group(self, objects, name="group"):
        models = []
        for o in objects:
            if not isinstance(o, ViewProxy):
                raise TypeError("add_group(): objects must be a list of objects")
            if o._model.type not in ["card", "stack"] and o._model.GetCard() == self._model:
                models.append(o._model)

        model = self._model
        if not model: return None

        @RunOnMainSync
        def func():
            if model.didSetDown: return None
            g = model.stackManager.GroupModelsInternal(models, name=name)
            return g.GetProxy() if g else None
        return func()

    def stop_all_animating(self, property_name=None):
        model = self._model
        if not model: return
        model.StopAnimation(property_name)
        for child in model.GetAllChildModels():
            child.StopAnimation(property_name)
