import threading

import wx
import ast
import re
import generator
import helpData
from time import time
from killableThread import RunOnMain
from cardstockFrameParts import *


class UiView(object):
    """
    This class is an abstract base class for the other Ui objects (view controllers) that coordinate management of
    their views and models.
    """

    def __init__(self, parent, stackManager, model, view):
        super().__init__()
        self.stackManager = stackManager
        self.parent = parent
        self.view = view
        self.model = None
        self.SetModel(model)
        self.hitRegion = None
        self.isSelected = False
        self.hasMouseMoved = False
        self.SetView(view)

        self.lastEditedHandler = None
        self.delta = ((0, 0))

    def __repr__(self):
        return "<"+str(self.__class__.__name__) + ":" + self.model.type + ":'" + self.model.GetProperty("name")+"'>"

    def BindEvents(self, view):
        view.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        view.Bind(wx.EVT_LEFT_DCLICK, self.FwdOnMouseDown)
        view.Bind(wx.EVT_MOTION, self.FwdOnMouseMove)
        view.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseUp)
        view.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        view.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

    def FwdOnMouseDown( self, event): self.stackManager.OnMouseDown( self, event)
    def FwdOnMouseMove( self, event): self.stackManager.OnMouseMove( self, event)
    def FwdOnMouseUp(   self, event): self.stackManager.OnMouseUp(   self, event)
    def FwdOnKeyDown(   self, event): self.stackManager.OnKeyDown(   self, event)
    def FwdOnKeyUp(     self, event): self.stackManager.OnKeyUp(     self, event)

    def SetView(self, view):
        self.view = view
        if view:
            self.BindEvents(view)
            view.Bind(wx.EVT_SIZE, self.OnResize)

            if self.GetCursor():
                self.view.SetCursor(wx.Cursor(self.GetCursor()))

            mSize = self.model.GetProperty("size")
            if mSize[0] > 0 and mSize[1] > 0:
                rect = wx.Rect(wx.Point(self.model.GetAbsolutePosition()), mSize)
                self.view.SetRect(self.stackManager.ConvRect(rect))

            self.view.Show(not self.model.GetProperty("hidden"))

    def SetModel(self, model):
        self.model = model
        self.lastEditedHandler = None

    def GetCursor(self):
        if self.stackManager.isEditing:
            return wx.CURSOR_HAND
        else:
            return None

    def OnPropertyChanged(self, model, key):
        if key == "size":
            s = self.model.GetProperty(key)
            self.ClearHitRegion()
            if self.view:
                rect = wx.Rect(wx.Point(self.model.GetAbsolutePosition()), s)
                self.view.SetRect(self.stackManager.ConvRect(rect))
                self.view.Refresh(True)
            else:
                self.stackManager.view.Refresh(True)
        elif key == "position":
            pos = wx.Point(self.model.GetAbsolutePosition())
            if self.view:
                rect = wx.Rect(pos, self.model.GetProperty("size"))
                self.view.SetRect(self.stackManager.ConvRect(rect))
                self.view.Refresh(True)
            else:
                self.stackManager.view.Refresh(True)
            if self.parent.model.type == "group":
                self.parent.ClearHitRegion()
        elif key == "hidden":
            if self.view:
                self.view.Show(not self.model.GetProperty(key))
            self.stackManager.view.Refresh(True)

    def OnResize(self, event):
        pass

    def DestroyView(self):
        if self.view:
            if self.view.HasCapture():
                self.view.ReleaseMouse()
            wx.CallAfter(self.view.Destroy)
            self.view = None

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        if self.isSelected != selected:
            self.isSelected = selected
            self.ClearHitRegion()
            self.stackManager.view.Refresh(True)

    def OnMouseDown(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnMouseDown"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseDown", event)
        event.Skip()

    def OnMouseMove(self, event):
        self.hasMouseMoved = True
        event.Skip()

    def OnMouseUp(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnMouseUp"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseUp", event)
        event.Skip()

    def OnMouseEnter(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnMouseEnter"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseEnter", event)
        event.Skip()

    def OnMouseExit(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnMouseExit"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseExit", event)
        event.Skip()

    def RunAnimations(self, onFinishedCalls):
        # Determine elapsed time since last OnIdle call to this object
        elapsedTime = 0
        now = time()
        if self.model.lastIdleTime:
            elapsedTime = now - self.model.lastIdleTime

            # Move the object by speed.x and speed.y pixels per second
            if self.model.type not in ["stack", "card"]:
                speed = self.model.GetProperty("speed")
                if speed != (0,0):
                    isAnimatingPos = False
                    for anim in self.model.animations:
                        if anim["type"] == "position":
                            isAnimatingPos = True
                    if not isAnimatingPos:
                        pos = self.model.GetProperty("position")
                        self.model.SetProperty("position", [pos.x + speed.x*elapsedTime, pos.y + speed.y*elapsedTime])

            # Run any in-progress animations
            for anim in self.model.animations.copy():
                progress = (now - anim["startTime"]) / anim["duration"]
                if progress < 1:
                    if anim["function"]:
                        anim["function"](progress)
                else:
                    if anim["function"]:
                        anim["function"](1.0)
                    self.model.animations.remove(anim)
                    if anim["onFinished"]:
                        onFinishedCalls.append(anim["onFinished"])

    def OnIdle(self, event):
        didRun = False
        if self.hasMouseMoved:
            self.hasMouseMoved = False
            if self.stackManager.runner and self.model.GetHandler("OnMouseMove"):
                self.stackManager.runner.RunHandler(self.model, "OnMouseMove", event)
                didRun = True

        # Determine elapsed time since last OnIdle call to this object
        elapsedTime = 0
        now = time()
        if self.model.lastIdleTime:
            elapsedTime = now - self.model.lastIdleTime
            # if self.model.type == "card" and elapsedTime>0.0: print(int(1.0/elapsedTime+0.5)) # print fps
            if self.stackManager.runner and self.model.GetHandler("OnIdle"):
                self.stackManager.runner.RunHandler(self.model, "OnIdle", event, elapsedTime)
                didRun = True

        self.model.lastIdleTime = now
        return didRun

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Inflate(2))

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            for box in self.GetResizeBoxRects():
                gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def Paint(self, gc):
        pass

    def HitTest(self, pt):
        if not self.hitRegion:
            self.MakeHitRegion()
        if self.hitRegion.Contains(pt):
            return self
        return None

    def GetResizeBoxRects(self):
        # The returned rects are relative to the position of the object
        # The resize box/handles should hang out of the frame, to allow grabbing it from behind
        # native widgets which can obscure the full frame.
        s = self.model.GetProperty("size")
        return [wx.Rect(-6, -6, 12, 12),
                wx.Rect(s.width - 4, -6, 12, 12),
                wx.Rect(-6, s.height - 4, 12, 12),
                wx.Rect(s.width - 4, s.height - 4, 12, 12)]

    def ClearHitRegion(self):
        self.hitRegion = None
        if self.parent and self.parent.model.type == "group":
            self.parent.ClearHitRegion()

    def GetHitRegion(self):
        if not self.hitRegion:
            self.MakeHitRegion()
        return self.hitRegion

    def MakeHitRegion(self):
        s = self.model.GetProperty("size")
        reg = wx.Region(wx.Rect(0, 0, s.width, s.height))
        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            for r in self.GetResizeBoxRects():
                reg.Union(wx.Region(r.Inflate(2)))
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
        'OnResize':     "OnResize():",
        'OnIdle':       "OnIdle(elapsedTime):",
    }


class ViewModel(object):
    """
    This is the abstract base class for the other model classes.
    The model holds the property values and event handler text for each object.
    It also holds the type of each property, and the ordered list of properties to display in the inspector.
    It also handles animating properties of the object, like position, size, or color.
    """

    minSize = wx.Size(20, 20)
    reservedNames = helpData.HelpData.ReservedNames()

    def __init__(self, stackManager):
        super().__init__()
        self.type = None
        self.parent = None
        self.handlers = {"OnSetup": "",
                         "OnMouseEnter": "",
                         "OnMouseDown": "",
                         "OnMouseMove": "",
                         "OnMouseUp": "",
                         "OnMouseExit": "",
                         "OnMessage": "",
                         "OnIdle": ""
                         }
        self.initialEditHandler = "OnMouseDown"

        self.properties = {"name": "",
                           "size": wx.Size(0,0),
                           "position": wx.RealPoint(0,0),
                           "speed": wx.Point(0,0),
                           "hidden": False,
                           "data": {}
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "floatpoint",
                              "center": "floatpoint",
                              "size": "size",
                              "speed": "point",
                              "hidden": "bool",
                              "data": "dict"
                              }
        self.propertyChoices = {}

        self.childModels = []
        self.stackManager = stackManager
        self.isDirty = False
        self.proxy = None
        self.lastIdleTime = None
        self.animations = []
        self.proxyClass = ViewProxy

    def __repr__(self):
        return "<"+str(self.__class__.__name__) + ":" + self.type + ":'" + self.GetProperty("name")+"'>"

    def CreateCopy(self):
        data = self.GetData()
        newModel = generator.StackGenerator.ModelFromData(self.stackManager, data)
        if newModel.type != "card":
            self.stackManager.uiCard.model.DeduplicateNamesForModels([newModel])
        else:
            newModel.SetProperty("name", newModel.DeduplicateName("card_1",
                                                                  [m.GetProperty("name") for m in self.stackManager.stackModel.childModels]))
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
                        "poly": "Polygon",
                        "roundrect": "Round Rectangle",
                        "group": "Group"}
        return displayTypes[self.type]

    def SetDirty(self, isDirty):
        self.isDirty = isDirty

    def GetDirty(self):
        return self.isDirty

    def GetPath(self):
        parts = []
        m = self
        while m.parent:
            parts.append(m.GetProperty("name"))
            m = m.parent
        return ".".join(reversed(parts))

    def SetStackView(self, stackManager):
        self.stackManager = stackManager
        for m in self.childModels:
            m.SetStackView(stackManager)

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

    def SetFrame(self, rect):
        self.SetProperty("position", rect.Position)
        self.SetProperty("size", rect.Size)

    def GetData(self):
        handlers = {}
        for k, v in self.handlers.items():
            if len(v.strip()) > 0:
                handlers[k] = v

        props = self.properties.copy()
        props.pop("hidden")
        props.pop("speed")
        for k,v in self.propertyTypes.items():
            if v in ["point", "floatpoint", "size"] and k in props:
                props[k] = list(props[k])
            elif v == "dict":
                props[k] = self.SanitizeDict(props[k], [])

        if len(props["data"]) == 0:
            props.pop("data")

        return {"type": self.type,
                "handlers": handlers,
                "properties": props}

    # These Sanitize* methods make sure that the "data" property only includes json-serializable data
    def SanitizeKey(self, val, seen):
        if type(val) == dict:
            value = None
        else:
            value = self.SanitizeValue(val, seen)
        return value

    def SanitizeValue(self, val, seen):
        if type(val) in [bool, int, float, str, None]:
            value = val
        elif isinstance(val, (wx.Point, wx.RealPoint, wx.Size, CDSPoint, CDSRealPoint, CDSSize)):
            value = self.SanitizeList(list(val), seen)
        elif type(val) == dict:
            if val not in seen:
                value = self.SanitizeDict(val, seen)
            else:
                value = None
        elif type(val) in [list, set, tuple]:
            if val not in seen:
                value = self.SanitizeList(list(val), seen)
            else:
                value = None
        else:
            try:
                value = str(val)
            except (ValueError, TypeError) as e:
                value = None
        return value

    def SanitizeDict(self, inDict, seen):
        seen.append(inDict)
        outDict = {}
        for k,v in inDict.items():
            key = self.SanitizeKey(k, seen)
            value = self.SanitizeValue(v, seen)
            if key is not None and value is not None:
                outDict[key] = value
        return outDict

    def SanitizeList(self, inList, seen):
        seen.append(inList)
        outList = []
        for v in inList:
            value = self.SanitizeValue(v, seen)
            if value is not None:
                outList.append(value)
        return outList

    def SetData(self, data):
        for k, v in data["handlers"].items():
            self.handlers[k] = v
        for k, v in data["properties"].items():
            if k in self.propertyTypes:
                if self.propertyTypes[k] == "point":
                    self.SetProperty(k, wx.Point(v), notify=False)
                elif self.propertyTypes[k] == "floatpoint":
                    self.SetProperty(k, wx.RealPoint(v[0], v[1]), notify=False)
                elif self.propertyTypes[k] == "size":
                    self.SetProperty(k, wx.Size(v), notify=False)
                else:
                    self.SetProperty(k, v, notify=False)

    def SetFromModel(self, model):
        for k, v in model.handlers.items():
            self.handlers[k] = v
        for k, v in model.properties.items():
            if self.propertyTypes[k] == "point":
                self.SetProperty(k, wx.Point(v), notify=False)
            elif self.propertyTypes[k] == "floatpoint":
                self.SetProperty(k, wx.RealPoint(v[0], v[1]), notify=False)
            elif self.propertyTypes[k] == "size":
                self.SetProperty(k, wx.Size(v), notify=False)
            else:
                self.SetProperty(k, v, notify=False)

    # Custom property order and mask for the inspector
    def PropertyKeys(self):
        if self.parent and self.parent.type == 'group':
            keys = self.propertyKeys.copy()
            keys.remove('position')
            keys.remove('size')
            return keys
        return self.propertyKeys

    # Options currently are string, bool, int, float, point, floatpoint, size, choice, color, file
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

    def GetChildModelByName(self, name):
        if self.properties["name"] == name:
            return self
        for child in self.childModels:
            result = child.GetChildModelByName(name)
            if result:
                return result
        return None

    def GetCard(self):
        if self.type == 'stack':
            return None
        if self.type == "card":
            return self
        if not self.parent:
            return None

        m = self
        while m.parent and m.type != 'card':
            m = m.parent
        return m

    def GetProperties(self):
        return self.properties

    def GetHandlers(self):
        return self.handlers

    def PerformFlips(self, fx, fy):
        pass

    def OrderMoveTo(self, index):
        index = index % len(self.parent.childModels) # Convert negative index to positive
        if index < 0 or index > len(self.parent.childModels)-1:
            return
        self.parent.childModels.remove(self)
        self.parent.childModels.insert(index, self)
        if self.GetCard() == self.stackManager.uiCard.model:
            self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)

    def OrderMoveBy(self, delta):
        index = self.parent.childModels.index(self) + delta
        self.OrderMoveTo(index)

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
        self.stackManager.OnPropertyChanged(self, key)

    @RunOnMain
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
                if not isinstance(val, (list, tuple)) or len(val) != 2:
                    raise Exception()
            elif propType == "size":
                val = ast.literal_eval(valStr)
                if not isinstance(val, (list, tuple)) or len(val) != 2:
                    raise Exception()
        except:
            return None
        return val

    def SetHandler(self, key, value):
        if self.handlers[key] != value:
            self.handlers[key] = value
            self.isDirty = True

    def AddAnimation(self, type, duration, func, onFinished=None, onCanceled=None):
        for d in self.animations.copy():
            if d["type"] == type:
                self.animations.remove(d)
                if "onCanceled" in d and d["onCanceled"]:
                    d["onCanceled"]()
        self.animations.append({"type":type,
                                "duration": duration,
                                "startTime": time(),
                                "function": func,
                                "onFinished": onFinished,
                                "onCanceled": onCanceled})

    def StopAnimations(self):
        for animation in self.animations:
            if "onCanceled" in animation and animation["onCanceled"]:
                animation["onCanceled"]()
        self.animations = []

    def DeduplicateName(self, name, existingNames):
        existingNames.extend(self.reservedNames) # disallow globals
        if name in existingNames:
            name = name.rstrip("0123456789_")
            name = self.GetNextAvailableName(name, existingNames)
        return name

    def GetNextAvailableName(self, base, existingNames):
        i = 0
        if base[-1] != "_":
            base += "_"
        while True:
            i += 1
            name = base+str(i)
            if name not in existingNames:
                return name

    def GetProxy(self):
        if not self.proxy:
            self.proxy = self.proxyClass(self)
        return self.proxy

    def RunSetup(self, runner):
        if self.type == "card":
            runner.SetupForCard(self)
        if self.GetHandler("OnSetup"):
            runner.RunHandler(self, "OnSetup", None)
        for m in self.childModels:
            m.RunSetup(runner)


class ViewProxy(object):
    """
    This class and its subclasses are the user-accessible objects exposed to event handler code.
    They purposefully contain no attributes for users to avoid, except a single _model reference.
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
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        if self._model.stackManager.runner:
            self._model.stackManager.runner.RunHandler(self._model, "OnMessage", None, message)

    @RunOnMain
    def Focus(self):
        if self._model.stackManager.runner:
            self._model.stackManager.runner.SetFocus(self)

    @property
    @RunOnMain
    def hasFocus(self):
        uiView = self._model.stackManager.GetUiViewByModel(self._model)
        if uiView and uiView.view:
            return uiView.view.HasFocus()

    @RunOnMain
    def Clone(self, **kwargs):
        if self._model.type != "card":
            newModel = self._model.CreateCopy()
            if not self.visible:
                newModel.SetProperty("hidden", True)
            for k,v in kwargs.items():
                if k in newModel.propertyTypes:
                    newModel.SetProperty(k, v)
            self._model.stackManager.AddUiViewsFromModels([newModel], False)
            self._model.stackManager.runner.SetupForCard(newModel.GetCard())

            newModel.RunSetup(self._model.stackManager.runner)
            if newModel.GetCard() != self._model.stackManager.uiCard.model:
                self._model.stackManager.runner.SetupForCard(self._model.stackManager.uiCard.model)
        else:
            newModel = self._model.stackManager.DuplicateCard()
            for k,v in kwargs.items():
                if k in newModel.propertyTypes:
                    newModel.SetProperty(k, v)

        return newModel.GetProxy()

    @RunOnMain
    def Delete(self):
        if self._model.type != "card":
            self._model.stackManager.RemoveUiViewByModel(self._model)
        else:
            self._model.stackManager.RemoveCardRaw(self._model)

    @RunOnMain
    def Cut(self):
        self._model.stackManager.CutModels([self._model], False)

    @RunOnMain
    def Copy(self):
        self._model.stackManager.CopyModels([self._model])
    #   Paste is in the runner

    @property
    def name(self):
        return self._model.GetProperty("name")

    @property
    def type(self):
        return self._model.type

    @property
    def data(self):
        return self._model.GetProperty("data")

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
        try:
            val = wx.Size(val[0], val[1])
        except:
            raise ValueError("size must be a size or a list of two numbers")
        self._model.SetProperty("size", val)

    @property
    def position(self):
        return CDSRealPoint(self._model.GetAbsolutePosition(), model=self._model, role="position")
    @position.setter
    def position(self, val):
        try:
            val = wx.RealPoint(val[0], val[1])
        except:
            raise ValueError("position must be a point or a list of two numbers")
        self._model.SetAbsolutePosition(val)

    @property
    def speed(self):
        speed = CDSPoint(self._model.GetProperty("speed"), model=self._model, role="speed")
        return speed
    @speed.setter
    def speed(self, val):
        try:
            val = wx.RealPoint(val[0], val[1])
        except:
            raise ValueError("speed must be a point or a list of two numbers")
        self._model.SetProperty("speed", val)

    @property
    def center(self):
        return CDSRealPoint(self._model.GetCenter(), model=self._model, role="center")
    @center.setter
    def center(self, center):
        try:
            center = wx.RealPoint(center[0], center[1])
        except:
            raise ValueError("center must be a point or a list of two numbers")
        self._model.SetCenter(center)

    @RunOnMain
    def FlipHorizontal(self):
        self._model.PerformFlips(True, False)

    @RunOnMain
    def FlipVertical(self):
        self._model.PerformFlips(False, True)

    @RunOnMain
    def OrderToFront(self):
        self._model.OrderMoveTo(-1)

    @RunOnMain
    def OrderForward(self):
        self._model.OrderMoveBy(1)

    @RunOnMain
    def OrderBackward(self):
        self._model.OrderMoveBy(-1)

    @RunOnMain
    def OrderToBack(self):
        self._model.OrderMoveTo(0)

    def OrderToIndex(self, i):
        if not isinstance(i, int):
            raise TypeError("i must be a number")

        @RunOnMain
        def f():
            self._model.OrderMoveTo(i)
        f()

    def Show(self):
        self.visible = True
    def Hide(self):
        self.visible = False

    @property
    def visible(self):
        return not self._model.GetProperty("hidden")
    @visible.setter
    def visible(self, val):
        self._model.SetProperty("hidden", not bool(val))

    @property
    def eventHandlers(self):
        return self._model.handlers

    def IsTouchingPoint(self, point):
        if not isinstance(point, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
            raise TypeError("point needs to be a point or a list of two numbers")
        if len(point) != 2:
            raise TypeError("point needs to be a point or a list of two numbers")
        try:
            int(point[0]), int(point[1])
        except:
            raise ValueError("point needs to be a point or a list of two numbers")

        @RunOnMain
        def f():
            sreg = self._model.stackManager.GetUiViewByModel(self._model).GetHitRegion()
            sreg = wx.Region(sreg)
            sreg.Offset(*self._model.GetProperty("position"))
            return sreg.Contains(wx.Point(point)) == wx.InRegion
        return f()

    def IsTouching(self, obj):
        if not isinstance(obj, ViewProxy):
            raise TypeError("obj must be a CardStock object")

        @RunOnMain
        def f():
            sreg = self._model.stackManager.GetUiViewByModel(self._model).GetHitRegion()
            oreg = self._model.stackManager.GetUiViewByModel(obj._model).GetHitRegion()
            sreg = wx.Region(sreg)
            oreg = wx.Region(oreg)
            sreg.Offset(*self._model.GetProperty("position"))
            oreg.Offset(*obj._model.GetProperty("position"))
            sreg.Intersect(oreg)
            return not sreg.IsEmpty()
        return f()

    def IsTouchingEdge(self, obj):
        if not isinstance(obj, ViewProxy):
            raise TypeError("obj must be a CardStock object")

        @RunOnMain
        def f():
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
        return f()

    def AnimatePosition(self, duration, endPosition, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        try:
            endPosition = wx.RealPoint(endPosition)
        except:
            raise ValueError("endPosition must be a point or a list of two numbers")

        @RunOnMain
        def func():
            origPosition = self._model.GetAbsolutePosition()
            if wx.Point(origPosition) != wx.Point(endPosition):
                offsetp = endPosition - origPosition
                offset = wx.RealPoint(offsetp[0], offsetp[1])

                def internalOnFinished():
                    self._model.SetProperty("speed", (0,0))
                    if onFinished: onFinished(*args, **kwargs)

                def onCanceled():
                    self._model.SetProperty("speed", (0,0))

                def f(progress):
                    self._model.SetAbsolutePosition(origPosition + offset * progress)
                self._model.AddAnimation("position", duration, f, internalOnFinished, onCanceled)
                self._model.SetProperty("speed", offset*(1.0/duration))
            else:
                def internalOnFinished():
                    if onFinished: onFinished(*args, **kwargs)
                self._model.AddAnimation("position", duration, None, internalOnFinished)
                self._model.SetProperty("speed", (0,0))
        func()

    def AnimateCenter(self, duration, endCenter, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        try:
            endCenter = wx.RealPoint(endCenter)
        except:
            raise ValueError("endCenter must be a point or a list of two numbers")

        @RunOnMain
        def func():
            origCenter = self._model.GetCenter()
            if wx.Point(origCenter) != wx.Point(endCenter):
                offsetp = endCenter - origCenter
                offset = wx.RealPoint(offsetp[0], offsetp[1])

                def internalOnFinished():
                    self._model.SetProperty("speed", (0,0))
                    if onFinished: onFinished(*args, **kwargs)

                def onCanceled():
                    self._model.SetProperty("speed", (0,0))

                def f(progress):
                    self._model.SetCenter(origCenter + offset * progress)
                self._model.AddAnimation("position", duration, f, internalOnFinished, onCanceled)
                self._model.SetProperty("speed", offset*(1.0/duration))
            else:
                def internalOnFinished():
                    if onFinished: onFinished(*args, **kwargs)
                self._model.AddAnimation("position", duration, None, internalOnFinished)
                self._model.SetProperty("speed", (0,0))
        func()

    def AnimateSize(self, duration, endSize, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        try:
            endSize = wx.Size(endSize)
        except:
            raise ValueError("endSize must be a size or a list of two numbers")

        @RunOnMain
        def func():
            def internalOnFinished():
                if onFinished: onFinished(*args, **kwargs)

            origSize = self._model.GetProperty("size")
            if wx.Size(origSize) != endSize:
                offset = wx.Size(endSize-origSize)
                def f(progress):
                    self._model.SetProperty("size", origSize + offset * progress)
                self._model.AddAnimation("size", duration, f, internalOnFinished)
            else:
                self._model.AddAnimation("size", duration, None, internalOnFinished)
        func()

    @RunOnMain
    def StopAnimations(self):
        self._model.StopAnimations()
