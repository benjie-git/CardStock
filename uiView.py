#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
import ast
import re
import generator
from time import time
import keyword


class UiView(object):
    def __init__(self, parent, stackView, model, view):
        super().__init__()
        self.stackView = stackView
        self.parent = parent
        self.view = view
        self.model = None
        self.doNotCache = False
        self.SetModel(model)
        self.hitRegion = None
        self.isSelected = False

        self.SetView(view)

        self.lastEditedHandler = None
        self.delta = ((0, 0))

    def __repr__(self):
        return "<"+str(self.__class__.__name__) + ":" + self.model.type + ":'" + self.model.GetProperty("name")+"'>"

    def BindEvents(self, view):
        view.Bind(wx.EVT_ENTER_WINDOW, self.FwdOnMouseEnter)
        view.Bind(wx.EVT_LEAVE_WINDOW, self.FwdOnMouseExit)
        view.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        view.Bind(wx.EVT_LEFT_DCLICK, self.FwdOnMouseDown)
        view.Bind(wx.EVT_MOTION, self.FwdOnMouseMove)
        view.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseUp)
        view.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        view.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

    def FwdOnMouseDown( self, event): self.stackView.OnMouseDown( self, event)
    def FwdOnMouseMove( self, event): self.stackView.OnMouseMove( self, event)
    def FwdOnMouseUp(   self, event): self.stackView.OnMouseUp(   self, event)
    def FwdOnMouseEnter(self, event): self.stackView.OnMouseEnter(self, event)
    def FwdOnMouseExit( self, event): self.stackView.OnMouseExit( self, event)
    def FwdOnKeyDown(   self, event): self.stackView.OnKeyDown(   self, event)
    def FwdOnKeyUp(     self, event): self.stackView.OnKeyUp(     self, event)

    def SetView(self, view):
        self.view = view
        if view:
            self.BindEvents(view)
            view.Bind(wx.EVT_SIZE, self.OnResize)

            if self.GetCursor():
                self.view.SetCursor(wx.Cursor(self.GetCursor()))

            mSize = self.model.GetProperty("size")
            if mSize[0] > 0 and mSize[1] > 0:
                self.view.SetSize(mSize)
                self.view.SetPosition(wx.Point(self.model.GetAbsolutePosition()))

            self.view.Show(not self.model.GetProperty("hidden"))

    def SetModel(self, model):
        self.model = model
        self.lastEditedHandler = None

    def GetCursor(self):
        return wx.CURSOR_HAND

    def OnPropertyChanged(self, model, key):
        if key in ["pre-size", "pre-position"]:
            self.stackView.Refresh(True, self.model.GetRefreshFrame())
        elif key == "size":
            s = self.model.GetProperty(key)
            self.hitRegion = None
            if self.view:
                self.view.SetSize(s)
                self.view.Refresh(True)
            else:
                self.stackView.Refresh(True, self.model.GetRefreshFrame())
        elif key == "position":
            pos = self.model.GetAbsolutePosition()
            if self.view:
                self.view.SetPosition(wx.Point(pos))
                self.view.Refresh(True)
            else:
                self.stackView.Refresh(True, self.model.GetRefreshFrame())
        elif key == "hidden":
            if self.view:
                self.view.Show(not self.model.GetProperty(key))

    def OnResize(self, event):
        pass

    def DestroyView(self):
        if self.view:
            self.view.Destroy()
            self.view = None

    def ReparentView(self, newParent):
        if self.view:
            self.view.Reparent(newParent)

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        self.isSelected = selected
        self.stackView.Refresh(True, self.model.GetRefreshFrame())

    def OnMouseDown(self, event):
        if self.stackView.runner and self.model.GetHandler("OnMouseDown"):
            self.stackView.runner.RunHandler(self.model, "OnMouseDown", event)
        event.Skip()

    def OnMouseMove(self, event):
        if self.stackView.runner and self.model.GetHandler("OnMouseMove"):
            self.stackView.runner.RunHandler(self.model, "OnMouseMove", event)
        event.Skip()

    def OnMouseUp(self, event):
        if self.stackView.runner and self.model.GetHandler("OnMouseUp"):
            self.stackView.runner.RunHandler(self.model, "OnMouseUp", event)
        event.Skip()

    def OnMouseEnter(self, event):
        if self.stackView.runner and self.model.GetHandler("OnMouseEnter"):
            self.stackView.runner.RunHandler(self.model, "OnMouseEnter", event)
        event.Skip()

    def OnMouseExit(self, event):
        if self.stackView.runner and self.model.GetHandler("OnMouseExit"):
            self.stackView.runner.RunHandler(self.model, "OnMouseExit", event)
        event.Skip()

    def OnIdle(self, event):
        # Determine elapsed time since last OnIdle call to this object
        elapsedTime = 0
        now = time()
        if self.model.lastIdleTime:
            elapsedTime = now - self.model.lastIdleTime
        self.model.lastIdleTime = now

        if elapsedTime:
            # Move the object by speed.x and speed.y pixels per second
            if self.model.type not in ["stack", "card"]:
                speed = self.model.properties["speed"]
                if speed != (0,0):
                    isAnimatingPos = False
                    for anim in self.model.animations:
                        if anim["type"] == "position":
                            isAnimatingPos = True
                    if not isAnimatingPos:
                        pos = self.model.properties["position"]
                        self.model.SetProperty("position", [pos.x + speed.x*elapsedTime, pos.y + speed.y*elapsedTime])

            # Run any in-progress animations
            for anim in self.model.animations.copy():
                if now < anim["startTime"] + anim["duration"]:
                    if anim["function"]:
                        progress = (now - anim["startTime"]) / anim["duration"]
                        anim["function"](progress)
                else:
                    if anim["function"]:
                        anim["function"](1.0)
                    self.model.animations.remove(anim)
                    if anim["onFinished"]:
                        wx.CallAfter(anim["onFinished"])

            if self.stackView.runner and self.model.GetHandler("OnIdle"):
                self.stackView.runner.RunHandler(self.model, "OnIdle", event, elapsedTime)

    def PaintSelectionBox(self, gc):
        if self.isSelected:
            f = self.model.GetAbsoluteFrame()
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Inflate(2))

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            box = self.GetResizeBoxRect()
            gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def Paint(self, gc):
        pass

    def HitTest(self, pt):
        if not self.hitRegion:
            self.MakeHitRegion()
        if self.hitRegion.Contains(pt):
            return self
        return None

    def GetResizeBoxRect(self):
        # the resize box/handle should hang out of the frame, to allow grabbing it from behind
        # native widgets which can obscure the full frame.
        s = self.model.GetProperty("size")
        return wx.Rect(s.width-4, s.height-4, 12, 12)

    def MakeHitRegion(self):
        s = self.model.GetProperty("size")
        reg = wx.Region(wx.Rect(0, 0, s.width, s.height))
        reg.Union(wx.Region(self.GetResizeBoxRect().Inflate(2)))
        self.hitRegion = reg

    handlerDisplayNames = {
        'OnSetup':      "OnSetup():",
        'OnShowCard':   "OnShowCard():",
        'OnHideCard':   "OnHideCard():",
        'OnClick':      "OnClick():",
        'OnTextEnter':  "OnTextEnter():",
        'OnTextChanged':"OnTextChanged():",
        'OnMouseDown':  "OnMouseDown(mousePos):",
        'OnMouseMove':  "OnMouseMove(mousePos):",
        'OnMouseUp':    "OnMouseUp(mousePos):",
        'OnMouseEnter': "OnMouseEnter(mousePos):",
        'OnMouseExit':  "OnMouseExit(mousePos):",
        'OnMessage':    "OnMessage(message):",
        'OnKeyDown':    "OnKeyDown(keyName):",
        'OnKeyUp':      "OnKeyUp(keyName):",
        'OnIdle':       "OnIdle(elapsedTime):",
    }


class ViewModel(object):
    minSize = wx.Size(20,20)
    reservedNames = ["eventHandlers", "stack", "card", "self", "keyName", "mousePos", "message", "bgColor", "index",
                     "name", "type", "position", "size", "center", "speed", "visible", "parent", "children",
                     "Cut", "Copy", "Paste", "Delete", "Clone", "Focus", "SendMessage", "Show", "Hide", "IsTouching",
                     "IsTouchingEdge", "AnimatePosition", "AnimateCenter", "AnimateSize", "StopAnimations",
                     "BroadcastMessage", "GotoCard", "GotoCardNumber", "GotoNextCard", "GotoPreviousCard",
                     "Wait", "Time", "Alert", "Ask", "PlaySound", "StopSound", "IsKeyPressed", "RunAfterDelay"]
    reservedNames.extend(keyword.kwlist)

    def __init__(self, stackView):
        super().__init__()
        self.type = None
        self.parent = None
        self.handlers = {"OnSetup": "",
                         "OnMouseDown": "",
                         "OnMouseMove": "",
                         "OnMouseUp": "",
                         "OnMouseEnter": "",
                         "OnMouseExit": "",
                         "OnMessage": "",
                         "OnIdle": ""
                         }
        self.properties = {"name": "",
                           "size": wx.Size(0,0),
                           "position": wx.RealPoint(0,0),
                           "speed": wx.Point(0,0),
                           "hidden": False,
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "floatpoint",
                              "center": "floatpoint",
                              "size": "size",
                              "speed": "point",
                              "hidden": "bool"}
        self.propertyChoices = {}

        self.childModels = []
        self.stackView = stackView
        self.isDirty = False
        self.proxy = None
        self.lastIdleTime = None
        self.animations = []
        self.proxyClass = ViewProxy

    def __repr__(self):
        return "<"+str(self.__class__.__name__) + ":" + self.type + ":'" + self.GetProperty("name")+"'>"

    def CreateCopy(self):
        data = self.GetData()
        newModel = generator.StackGenerator.ModelFromData(self.stackView, data)
        if newModel.type != "card":
            newModel.SetProperty("name", self.stackView.uiCard.model.DeduplicateNameInCard(newModel.GetProperty("name")))
        else:
            newModel.SetProperty("name", newModel.DeduplicateName("card_1",
                                                                  [m.GetProperty("name") for m in self.stackView.stackModel.childModels]))
        return newModel

    def GetType(self):
        return self.type

    def GetDisplayType(self):
        displayTypes = {"card": "Card",
                        "button": "Button",
                        "textfield": "TextField",
                        "textlabel": "TextLabel",
                        "image": "Image",
                        "pen": "Pen",
                        "line": "Line",
                        "rect": "Rectangle",
                        "oval": "Oval",
                        "round_rect": "Round Rectangle",
                        "group": "Group"}
        return displayTypes[self.type]

    def SetDirty(self, isDirty):
        self.isDirty = isDirty

    def GetDirty(self):
        return self.isDirty

    def SetStackView(self, stackView):
        self.stackView = stackView
        for m in self.childModels:
            m.SetStackView(stackView)

    def GetAbsolutePosition(self):
        p = self.GetProperty("position")
        pos = wx.RealPoint(p[0], p[1])  # Copy so we don't edit the model's position
        parent = self.parent
        while parent and parent.type != "card":
            parentPos = parent.GetProperty("position")
            pos += parentPos
            parent = parent.parent
        return pos

    def SetAbsolutePosition(self, pos):
        parent = self.parent
        pos = wx.RealPoint(pos[0], pos[1])
        while parent and parent.type != "card":
            parentPos = parent.GetProperty("position")
            pos -= parentPos
            parent = parent.parent
        self.SetProperty("position", pos)

    def GetCenter(self):
        return self.GetProperty("center")

    def SetCenter(self, center):
        self.SetProperty("center", center)

    def GetFrame(self):
        p = wx.Point(self.GetProperty("position"))
        s = self.GetProperty("size")
        return wx.Rect(p, s)

    def GetAbsoluteFrame(self):
        p = wx.Point(self.GetAbsolutePosition())
        s = self.GetProperty("size")
        return wx.Rect(p, s)

    def GetRefreshFrame(self):
        return self.GetAbsoluteFrame().Inflate(8)

    def SetFrame(self, rect):
        self.SetProperty("position", rect.Position)
        self.SetProperty("size", rect.Size)

    def GetData(self):
        handlers = {}
        for k, v in self.handlers.items():
            if len(v.strip()) > 0:
                handlers[k] = v

        props = self.properties.copy()
        for k,v in self.propertyTypes.items():
            if v in ["point", "floatpoint", "size"] and k in props:
                props[k] = list(props[k])
        props.pop("hidden")
        props.pop("speed")

        return {"type": self.type,
                "handlers": handlers,
                "properties": props}

    def SetData(self, data):
        for k, v in data["handlers"].items():
            self.handlers[k] = v
        for k, v in data["properties"].items():
            if k in self.propertyTypes:
                if self.propertyTypes[k] == "point":
                    self.SetProperty(k, wx.Point(v), False)
                elif self.propertyTypes[k] == "floatpoint":
                    self.SetProperty(k, wx.RealPoint(v[0], v[1]), False)
                elif self.propertyTypes[k] == "size":
                    self.SetProperty(k, wx.Size(v), False)
                else:
                    self.SetProperty(k, v, False)

    def SetFromModel(self, model):
        for k, v in model.handlers.items():
            self.handlers[k] = v
        for k, v in model.properties.items():
            if self.propertyTypes[k] == "point":
                self.SetProperty(k, wx.Point(v), False)
            elif self.propertyTypes[k] == "floatpoint":
                self.SetProperty(k, wx.RealPoint(v[0], v[1]), False)
            elif self.propertyTypes[k] == "size":
                self.SetProperty(k, wx.Size(v), False)
            else:
                self.SetProperty(k, v, False)

    # Custom property order and mask for the inspector
    def PropertyKeys(self):
        return self.propertyKeys

    # Options currently are string, bool, int, float, point, realpoint, size, choice
    def GetPropertyType(self, key):
        return self.propertyTypes[key]

    def GetPropertyChoices(self, key):
        return self.propertyChoices[key]

    def GetProperty(self, key):
        if key == "center":
            p = self.GetAbsolutePosition()
            s = self.GetProperty("size")
            center = [p.x + s.width / 2, p.y + s.height / 2]
            return center
        elif key in self.properties:
            return self.properties[key]
        return None

    def GetHandler(self, key):
        if key in self.handlers:
            return self.handlers[key]
        return None

    def GetProperties(self):
        return self.properties

    def GetHandlers(self):
        return self.handlers

    def FramePartChanged(self, cdsFramePart):
        if cdsFramePart.role == "position":
            self.SetAbsolutePosition(cdsFramePart)
        elif cdsFramePart.role == "size":
            self.SetProperty("size", cdsFramePart)
        elif cdsFramePart.role == "center":
            self.SetCenter(cdsFramePart)
        elif cdsFramePart.role == "speed":
            self.SetProperty("speed", cdsFramePart)

    def Notify(self, key):
        self.stackView.OnPropertyChanged(self, key)

    def SetProperty(self, key, value, notify=True):
        if key in self.propertyTypes and self.propertyTypes[key] == "point" and not isinstance(value, wx.Point):
            value = wx.Point(value)
        elif key in self.propertyTypes and self.propertyTypes[key] == "floatpoint" and not isinstance(value, wx.RealPoint):
            value = wx.RealPoint(value[0], value[1])
        elif key in self.propertyTypes and self.propertyTypes[key] == "size" and not isinstance(value, wx.Point):
            value = wx.Size(value)
        elif key in self.propertyTypes and self.propertyTypes[key] == "choice" and value not in self.propertyChoices[key]:
            return

        if key == "name":
            value = re.sub(r'\W+', '', value)
            if not re.match(r'[A-Za-z][A-Za-z_0-9]*', value):
                if notify:
                    self.Notify(key)
                return
        elif key == "size":
            if value.width < self.minSize.width: value.width = self.minSize.width
            if value.height < self.minSize.height: value.height = self.minSize.height
        elif key == "center":
            s = self.GetProperty("size")
            self.SetAbsolutePosition([value.x - s.width / 2, value.y - s.height / 2])
            return

        if self.properties[key] != value:
            if notify:
                self.Notify("pre-"+key)
            self.properties[key] = value
            if notify:
                self.Notify(key)
            self.isDirty = True

    def InterpretPropertyFromString(self, key, valStr):
        propType = self.propertyTypes[key]
        val = valStr
        try:
            if propType == "bool":
                val = valStr == "True"
            elif propType == "int":
                val = int(valStr)
            elif propType == "float":
                val = float(valStr)
            elif propType in ["point", "floatpoint"]:
                val = ast.literal_eval(valStr)
                if not isinstance(val, list) or len(val) != 2:
                    raise Exception()
            elif propType == "size":
                val = ast.literal_eval(valStr)
                if not isinstance(val, list) or len(val) != 2:
                    raise Exception()
        except:
            return None
        return val

    def SetHandler(self, key, value):
        if self.handlers[key] != value:
            self.handlers[key] = value
            self.isDirty = True

    def AddAnimation(self, type, duration, func, onFinished=None):
        for d in self.animations.copy():
            if d["type"] == type:
                self.animations.remove(d)
        self.animations.append({"type":type,
                                "duration": duration,
                                "startTime": time(),
                                "function": func,
                                "onFinished": onFinished})

    def StopAnimations(self):
        self.animations = []

    def DeduplicateName(self, name, existingNames):
        existingNames.extend(self.reservedNames) # disallow globals
        if name in existingNames:
            name = name.rstrip("0123456789")
            if name[-1:] != "_":
                name = name + "_"
            name = self.GetNextAvailableName(name, existingNames)
        return name

    def GetNextAvailableName(self, base, existingNames):
        i = 0
        while True:
            i += 1
            name = base+str(i)
            if name not in existingNames:
                return name

    def GetProxy(self):
        if not self.proxy:
            self.proxy = self.proxyClass(self)
        return self.proxy


class ViewProxy(object):
    """
     This class and its subclasses are the user-accessible objects exposed in event handlers.
     They purposefully contain no attributes for users to mess with, except a single _model reference.
    """
    def __init__(self, model):
        super().__init__()
        self._model = model

    def __getattr__(self, item):
        for model in self._model.childModels:
            if model.properties["name"] == item:
                return model.GetProxy()
        return super().__getattribute__(item)

    def SendMessage(self, message):
        if self._model.stackView.runner:
            self._model.stackView.runner.RunHandler(self._model, "OnMessage", None, message)

    def Focus(self):
        if self._model.stackView.runner:
            self._model.stackView.runner.SetFocus(self)

    def Clone(self):
        newModel = self._model.CreateCopy()
        if newModel.type != "card":
            self._model.stackView.AddUiViewsFromModels([newModel], False)
        else:
            self._model.stackView.DuplicateCard()
        return newModel.GetProxy()

    def Delete(self):
        if self._model.type != "card":
            self._model.stackView.RemoveUiViewByModel(self._model)
        else:
            self._model.stackView.RemoveCard()

    def Cut(self): self._model.stackView.CutModels([self._model], False)
    def Copy(self): self._model.stackView.CopyModels([self._model])
    #   Paste is in the runner

    @property
    def name(self):
        return self._model.GetProperty("name")

    @property
    def type(self):
        return self._model.type

    @property
    def parent(self):
        parent = self._model.parent
        if parent: parent = parent.GetProxy()
        return parent

    @property
    def children(self):
        return [m.GetProxy() for m in self._model.childModels]

    @property
    def size(self):
        return CDSSize(self._model.GetProperty("size"), model=self._model, role="size")
    @size.setter
    def size(self, val):
        self._model.SetProperty("size", wx.Size(val))

    @property
    def position(self):
        return CDSRealPoint(self._model.GetAbsolutePosition(), model=self._model, role="position")
    @position.setter
    def position(self, val):
        self._model.SetAbsolutePosition(wx.RealPoint(val[0], val[1]))

    @property
    def speed(self):
        speed = CDSPoint(self._model.GetProperty("speed"), model=self._model, role="speed")
        return speed
    @speed.setter
    def speed(self, val):
        self._model.SetProperty("speed", val)

    @property
    def center(self):
        return CDSRealPoint(self._model.GetCenter(), model=self._model, role="center")
    @center.setter
    def center(self, center):
        self._model.SetCenter(wx.RealPoint(center[0], center[1]))

    def Show(self): self._model.SetProperty("hidden", False)
    def Hide(self): self._model.SetProperty("hidden", True)
    @property
    def visible(self):
        return not self._model.GetProperty("hidden")
    @visible.setter
    def visible(self, val):
        self._model.SetProperty("hidden", not bool(val))

    @property
    def eventHandlers(self):
        return self._model.handlers

    def IsTouching(self, obj):
        sf = self._model.GetAbsoluteFrame() # self frame in card coords
        f = obj._model.GetAbsoluteFrame() # other frame in card soords
        return sf.Intersects(f)

    def IsTouchingEdge(self, obj):
        sf = self._model.GetAbsoluteFrame() # self frame in card coords
        f = obj._model.GetAbsoluteFrame() # other frame in card soords
        top = wx.Rect(f.Left, f.Top, f.Width, 1)
        bottom = wx.Rect(f.Left, f.Bottom, f.Width, 1)
        left = wx.Rect(f.Left, f.Top, 1, f.Height)
        right = wx.Rect(f.Right, f.Top, 1, f.Height)
        if sf.Intersects(top): return "Top"
        if sf.Intersects(bottom): return "Bottom"
        if sf.Intersects(left): return "Left"
        if sf.Intersects(right): return "Right"
        return None

    def AnimatePosition(self, duration, endPosition, onFinished=None):
        origPosition = self.position
        endPosition = wx.RealPoint(endPosition)
        if wx.Point(origPosition) != wx.Point(endPosition):
            offsetp = endPosition - origPosition
            offset = wx.RealPoint(offsetp[0], offsetp[1])

            self._model.SetProperty("speed", offset*(1.0/duration))

            def internalOnFinished():
                self._model.SetProperty("speed", (0,0))
                if onFinished: onFinished()

            def f(progress):
                self.position = [origPosition.x + offset.x * progress,
                                 origPosition.y + offset.y * progress]
            self._model.AddAnimation("position", duration, f, internalOnFinished)
        else:
            self._model.AddAnimation("position", duration, None, onFinished)

    def AnimateCenter(self, duration, endCenter, onFinished=None):
        origCenter = self.center
        endCenter = wx.RealPoint(endCenter)
        if wx.Point(origCenter) != wx.Point(endCenter):
            offsetp = endCenter - origCenter
            offset = wx.RealPoint(offsetp[0], offsetp[1])

            self._model.SetProperty("speed", offset*(1.0/duration))

            def internalOnFinished():
                self._model.SetProperty("speed", (0,0))
                if onFinished: onFinished()

            def f(progress):
                self.center = [origCenter.x + offset.x * progress,
                               origCenter.y + offset.y * progress]
            self._model.AddAnimation("position", duration, f, internalOnFinished)
        else:
            self._model.AddAnimation("position", duration, None, onFinished)


    def AnimateSize(self, duration, endSize, onFinished=None):
        origSize = self.size
        if wx.Size(origSize) != wx.Size(endSize):
            offset = wx.Size(endSize-origSize)
            def f(progress):
                self.size = [origSize.width + offset.width * progress,
                               origSize.height + offset.height * progress]
            self._model.AddAnimation("size", duration, f, onFinished)
        else:
            self._model.AddAnimation("size", duration, None, onFinished)

    def StopAnimations(self):
        self._model.StopAnimations()


# CardStock-specific Point, Size, RealPoint subclasses
# These notify their model when their components are changed, so that, for example:
# button.center.x = 100  will notify the button's model that the center changed.
class CDSPoint(wx.Point):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model")
        role = kwargs.pop("role")
        super().__init__(*args, **kwargs)
        self.model = model
        self.role = role

    @property
    def x(self):
        return super().x
    @x.setter
    def x(self, val):
        self += [val-self.x, 0]
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return super().y
    @y.setter
    def y(self, val):
        self += [0, val-self.y]
        self.model.FramePartChanged(self)


class CDSRealPoint(wx.RealPoint):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model")
        role = kwargs.pop("role")
        super().__init__(*args, **kwargs)
        self.model = model
        self.role = role

    @property
    def x(self):
        return super().x
    @x.setter
    def x(self, val):
        self += [val-self.x, 0]
        self.model.FramePartChanged(self)

    @property
    def y(self):
        return super().y
    @y.setter
    def y(self, val):
        self += [0, val-self.y]
        self.model.FramePartChanged(self)


class CDSSize(wx.Size):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model")
        role = kwargs.pop("role")
        super().__init__(*args, **kwargs)
        self.model = model
        self.role = role

    @property
    def width(self):
        return super().width
    @width.setter
    def width(self, val):
        self += [val-self.width, 0]
        self.model.FramePartChanged(self)

    @property
    def height(self):
        return super().height
    @height.setter
    def height(self, val):
        self += [0, val-self.height]
        self.model.FramePartChanged(self)
