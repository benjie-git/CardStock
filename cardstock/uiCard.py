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
        self.uiViews = []
        super().__init__(parent, stackManager, model, stackManager.view)

    def DestroyView(self):
        if self.view:
            if self.view.HasCapture():
                self.view.ReleaseMouse()
            self.view = None

    def SetDown(self):
        for ui in self.uiViews:
            ui.SetDown()
        self.uiViews = None
        super().SetDown()

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

    def OnResize(self, event):
        if self.stackManager and (self.stackManager.isEditing or self.model.parent.GetProperty("canResize")):
            self.model.parent.SetProperty("size", self.view.GetSize())
        event.Skip()

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()
            f.Top += 1
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Deflate(1))

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            for box in self.GetResizeBoxRects():
                gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def GetResizeBoxRects(self):
        # the resize box/handle should hang out of the frame, to allow grabbing it from behind
        # native widgets which can obscure the full frame.
        s = self.model.GetProperty("size")
        return [wx.Rect(s.width-13, 0, 12, 12)]

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "name":
            self.stackManager.designer.UpdateCardList()
        elif key == "bgColor":
            self.view.Refresh()

    def OnKeyDown(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnKeyDown"):
            self.stackManager.runner.RunHandler(self.model, "OnKeyDown", event)

    def OnKeyUp(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnKeyUp"):
            self.stackManager.runner.RunHandler(self.model, "OnKeyUp", event)

    def OnPeriodic(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnKeyHold"):
            for keyName in self.stackManager.runner.pressedKeys:
                self.stackManager.runner.RunHandler(self.model, "OnKeyHold", event, keyName)
        didRun = False
        for child in reversed(self.GetAllUiViews()):
            if child.OnPeriodic(event):
                didRun = True
        if super().OnPeriodic(event):
            didRun = True
        return didRun


class CardModel(ViewModel):
    """
    The CardModel allows access to a few properties that actually live in the stack.  This is because the Designer
    allows editing cards, but not the stack model itself.  These properties are size, canSave, and canResize.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "card"
        self.proxyClass = Card
        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "", "OnShowCard": "", "OnHideCard": "", "OnKeyDown": "",
                    "OnKeyHold": "", "OnKeyUp": "", "OnResize":""}
        del self.handlers["OnBounce"]
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.handlers["OnExitStack"] = ""
        self.initialEditHandler = "OnSetup"

        # Custom property order and mask for the inspector
        self.properties["name"] = "card_1"
        self.properties["bgColor"] = "white"
        self.propertyKeys = ["name", "bgColor", "size", "canSave", "canResize"]

        self.propertyTypes["bgColor"] = "color"
        self.propertyTypes["canSave"] = 'bool'
        self.propertyTypes["canResize"] = 'bool'

    def SetProperty(self, key, value, notify=True):
        if key in ["size", "canSave", "canResize"]:
            self.parent.SetProperty(key, value, notify)
        else:
            super().SetProperty(key, value, notify)

    def GetProperty(self, key):
        if key in ["size", "canSave", "canResize"]:
            return self.parent.GetProperty(key)
        else:
            return super().GetProperty(key)

    def GetFrame(self):
        s = self.parent.GetProperty("size")
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
            m = generator.StackGenerator.ModelFromData(self.stackManager, childData)
            m.parent = self
            self.childModels.append(m)

    def AddChild(self, model):
        self.InsertChild(model, len(self.childModels))

    def InsertChild(self, model, index):
        self.childModels.insert(index, model)
        model.parent = self
        self.isDirty = True
        if self.stackManager.runner and self.stackManager.uiCard.model == self:
            self.stackManager.runner.SetupForCard(self)

    def RemoveChild(self, model):
        self.childModels.remove(model)
        model.SetDown()
        self.isDirty = True
        if self.stackManager.runner and self.stackManager.uiCard.model == self:
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
        cardSize = self.GetProperty("size")
        if fx or fy:
            for m in self.childModels:
                m.PerformFlips(fx, fy, notify=notify)
            for m in self.childModels:
                pos = m.GetProperty("position")
                size = m.GetProperty("size")
                pos = wx.Point((cardSize.width - (pos.x + size.width)) if fx else pos.x,
                               (cardSize.height - (pos.y + size.height)) if fy else pos.y)
                m.SetProperty("position", pos, notify=notify)
        if notify:
            self.Notify("size")

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
    def bgColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("bgColor")
    @bgColor.setter
    def bgColor(self, val):
        if not isinstance(val, str):
            raise TypeError("bgColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("bgColor", val)

    @property
    def number(self):
        model = self._model
        if not model: return -1
        return model.parent.childModels.index(model)+1

    def AnimateBgColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)
        if endColor.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.bgColor)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("bgColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

            def internalOnFinished(animDict):
                if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

            model.AddAnimation("bgColor", duration, onUpdate, onStart, internalOnFinished)

    def AddButton(self, name="button", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("button", name, (100,24), kwargs)
        return obj.GetProxy() if obj else None

    def AddTextField(self, name="field", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("textfield", name, (100,24), kwargs)
        return obj.GetProxy() if obj else None

    def AddTextLabel(self, name="label", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("textlabel", name, (100,24), kwargs)
        return obj.GetProxy() if obj else None

    def AddImage(self, name="image", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("image", name, (80,80), kwargs)
        return obj.GetProxy() if obj else None

    def AddOval(self, name="oval", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("oval", name, None, [(10, 10), (100, 100)], kwargs)
        return obj.GetProxy() if obj else None

    def AddRectangle(self, name="rect", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("rect", name, None, [(10, 10), (100, 100)], kwargs)
        return obj.GetProxy() if obj else None

    def AddRoundRectangle(self, name="roundrect", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("roundrect", name, None, [(10, 10), (100, 100)], kwargs)
        return obj.GetProxy() if obj else None

    def AddLine(self, points, name="line", **kwargs):
        if not isinstance(points, (list, tuple)):
            raise TypeError("points should be a list of points")
        if len(points) < 2:
            raise TypeError("points should be a list of at least 2 points")
        for p in points:
            if not isinstance(p, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
                raise TypeError("points items each need to be a point or a list of two numbers")
            if len(p) != 2:
                raise TypeError("points items each need to be a point or a list of two numbers")
            try:
                int(p[0]), int(p[1])
            except:
                raise ValueError("points items each need to be a point or a list of two numbers")

        model = self._model
        if not model: return None

        line = model.AddNewObject("line", name, None, points, kwargs)
        return line.GetProxy() if line else None

    def AddPolygon(self, points, name="polygon", **kwargs):
        if not isinstance(points, (list, tuple)):
            raise TypeError("points should be a list of points")
        if len(points) < 2:
            raise TypeError("points should be a list of at least 2 points")
        for p in points:
            if not isinstance(p, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
                raise TypeError("points items each need to be a point or a list of two numbers")
            if len(p) != 2:
                raise TypeError("points items each need to be a point or a list of two numbers")
            try:
                int(p[0]), int(p[1])
            except:
                raise ValueError("points items each need to be a point or a list of two numbers")

        model = self._model
        if not model: return None

        poly = model.AddNewObject("poly", name, None, points, kwargs)
        return poly.GetProxy() if poly else None

    def AddGroup(self, objects, name="group"):
        models = []
        for o in objects:
            if not isinstance(o, ViewProxy):
                raise TypeError("objects must be a list of objects")
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

    def StopAllAnimating(self, propertyName=None):
        model = self._model
        if not model: return
        model.StopAnimation(propertyName)
        for child in model.GetAllChildModels():
            child.StopAnimation(propertyName)
