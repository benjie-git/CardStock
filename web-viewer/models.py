import browser
import wx_compat as wx
import sanitizer
from time import time
from urllib.parse import urlparse
import math
import re

VERSION='0.9.8'
FILE_FORMAT_VERSION=3


class ViewModel(object):
    """
    This is the abstract base class for the other model classes.
    The model holds the property values and event handler text for each object.
    It also holds the type of each property, and the ordered list of properties to display in the inspector.
    It also handles animating properties of the object, like position, size, or color.
    """

    minSize = wx.Size(20, 20)
    reservedNames = ['keyName', 'mousePos', 'message', 'URL', 'didLoad', 'otherObject', 'edge', 'elapsedTime', 'self',
                     'stack', 'card', 'Wait', 'Distance', 'RunAfterDelay', 'Time', 'Paste', 'Alert', 'AskYesNo',
                     'AskText', 'GotoCard', 'GotoNextCard', 'GotoPreviousCard', 'RunStack', 'PlaySound', 'StopSound',
                     'BroadcastMessage', 'IsKeyPressed', 'IsMouseDown', 'GetMousePos', 'Color', 'Point', 'Size', 'Quit',
                     'name', 'type', 'data', 'position', 'size', 'center', 'rotation', 'speed', 'isVisible', 'hasFocus',
                     'parent', 'children', 'Copy', 'Cut', 'Clone', 'Delete', 'SendMessage', 'Focus', 'Show', 'Hide',
                     'ChildWithBaseName', 'FlipHorizontal', 'FlipVertical', 'OrderToFront', 'OrderForward',
                     'OrderBackward', 'OrderToBack', 'OrderToIndex', 'GetEventCode', 'SetEventCode',
                     'StopHandlingMouseEvent', 'IsTouching', 'SetBounceObjects', 'IsTouchingPoint', 'IsTouchingEdge',
                     'AnimatePosition', 'AnimateCenter', 'AnimateSize', 'AnimateRotation', 'StopAnimating', 'fillColor',
                     'number', 'canSave', 'canResize', 'AddButton', 'AddTextField', 'AddTextLabel', 'AddImage', 'AddOval',
                     'AddRectangle', 'AddRoundRectangle', 'AddLine', 'AddPolygon', 'AddGroup', 'AnimateFillColor',
                     'StopAllAnimating', 'numCards', 'currentCard', 'False', 'None', 'True', '__peg_parser__', 'and',
                     'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
                     'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
                     'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']

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
                         "OnBounce": "",
                         "OnMessage": "",
                         "OnPeriodic": ""
                         }
        self.initialEditHandler = "OnMouseDown"
        self.visibleHandlers = set()

        self.properties = {"name": "",
                           "size": wx.Size(0,0),
                           "position": wx.RealPoint(0,0),
                           "speed": wx.Point(0,0),
                           "isVisible": True,
                           "data": {}
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "floatpoint",
                              "center": "floatpoint",
                              "size": "size",
                              "speed": "point",
                              "isVisible": "bool",
                              "data": "dict"
                              }

        self.childModels = []
        self.stackManager = stackManager
        self.isDirty = False
        self.proxy = None
        self.lastOnPeriodicTime = None
        self.animations = {}
        self.bounceObjs = {}
        self.proxyClass = ViewProxy
        self.didSetDown = False
        self.clonedFrom = None

    def __repr__(self):
        return f"<{self.GetDisplayType()}:'{self.GetProperty('name')}'>"

    def SetBackUp(self, stackManager):
        if self.didSetDown:
            self.stackManager = stackManager
            self.didSetDown = False
            for child in self.childModels:
                child.SetBackUp(stackManager)
                child.parent = self

    def SetDown(self):
        self.didSetDown = True
        for child in self.childModels:
            child.SetDown()
        if self.proxy:
            self.proxy._model = None
            self.proxy = None
        self.animations = {}
        self.bounceObjs = {}
        self.stackManager = None
        self.parent = None

    def DismantleChildTree(self):
        for child in self.childModels:
            child.DismantleChildTree()
        self.childModels = None

    def CreateCopy(self, name=None):
        data = self.GetData()
        newModel = self.stackManager.ModelFromData(self.stackManager, data)
        newModel.clonedFrom = self.clonedFrom if self.clonedFrom else self
        if newModel.type != "card":
            if name:
                newModel.properties["name"] = name
            self.stackManager.uiCard.model.DeduplicateNamesForModels([newModel])
        else:
            if not name:
                name = "card_1"
            newModel.SetProperty("name", newModel.DeduplicateName(name,
                [m.GetProperty("name") for m in self.stackManager.stackModel.childModels]), notify=False)
        return newModel

    def GetDisplayType(self):
        displayTypes = {"card": "Card",
                        "button": "Button",
                        "textfield": "TextField",
                        "textlabel": "TextLabel",
                        "image": "Image",
                        "webview": "WebView",
                        "pen": "Pen",
                        "line": "Line",
                        "rect": "Rectangle",
                        "oval": "Oval",
                        "polygon": "Polygon",
                        "roundrect": "Round Rectangle",
                        "group": "Group",
                        "stack": "Stack"}
        return displayTypes[self.type]

    def SetDirty(self, isDirty):
        if isDirty:
            self.isDirty = True
        else:
            self.isDirty = False
            for child in self.childModels:
                child.SetDirty(False)

    def GetDirty(self):
        if self.isDirty:
            return True
        for card in self.childModels:
            if card.GetDirty():
                return True
        return False

    def CanRotate(self):
        return ("rotation" in self.properties)

    def GetPath(self):
        parts = []
        m = self
        while m.parent:
            parts.append(m.GetProperty("name"))
            m = m.parent
        return ".".join(reversed(parts))

    def SetStackManager(self, stackManager):
        self.stackManager = stackManager
        for m in self.childModels:
            m.SetStackManager(stackManager)

    def GetAffineTransform(self):
        # Get the transform that converts local coords to abs coords
        m = self
        ancestors = []
        aff = wx.AffineMatrix2D()
        while m and m.type not in ["card", "stack"]:
            ancestors.append(m)
            m = m.parent
        for m in reversed(ancestors):
            pos = m.GetProperty("position")
            size = m.GetProperty("size")
            rot = m.GetProperty("rotation")
            aff.Translate(*(pos + (int(size[0]/2), int(size[1]/2))))
            if rot:
                aff.Rotate(math.radians(-rot))
            aff.Translate(-int(size[0]/2), -int(size[1]/2))
        return aff

    def RotatedPoints(self, points, aff=None):
        # convert points in the local system to abs
        if aff is None:
            aff = self.GetAffineTransform()
        return [wx.RealPoint(aff.TransformPoint(*p)) for p in points]

    def RotatedRectPoints(self, rect, aff=None):
        # Convert local rect to absolute corner points
        points = [rect.TopLeft, rect.TopRight+(1,0), rect.BottomRight+(1,1), rect.BottomLeft+(0,1)]
        return self.RotatedPoints(points, aff)

    def RotatedRect(self, rect, aff=None):
        # Convert local rect to an absolute rect than contains the local one
        points = self.RotatedRectPoints(rect, aff)
        l2 = list(map(list, zip(*points)))
        rotSize = (max(l2[0]) - min(l2[0]) - 1, max(l2[1]) - min(l2[1]) - 1)
        rotPos_x, rotPos_y = (min(l2[0]), min(l2[1]))
        return wx.Rect(rotPos_x, rotPos_y, rotSize[0], rotSize[1])

    def UnrotatedRectFromAbsPoints(self, ptA, ptB):
        # Takes 2 absolute points, and creates a local rect
        # This is not fully general purpose: it assumes the parent is a card (not inside a group)
        # This is ok since you can't manually resize a child of a group, and this function is
        # only used from the resize path in the Select Tool.
        rot = self.GetProperty("rotation")
        center = (ptA + ptB)/2
        if rot:
            aff = wx.AffineMatrix2D()
            aff.Translate(*center)
            aff.Rotate(math.radians(rot))
            aff.Translate(*(wx.RealPoint(0,0)-wx.RealPoint(center)))
            ptA = aff.TransformPoint(*ptA)
            ptB = aff.TransformPoint(*ptB)

        bl = wx.Point(min(ptA[0], ptB[0]), min(ptA[1], ptB[1]))
        tr = wx.Point(max(ptA[0], ptB[0]), max(ptA[1], ptB[1]))
        return wx.Rect(bl, tr)

    def GetAbsolutePosition(self):
        parent = self.parent
        pos = self.GetProperty("position")
        if self.parent and (self.parent.type != "card" or self.GetProperty("rotation")):
            aff = parent.GetAffineTransform()
            pos = aff.TransformPoint(*pos)
        return wx.RealPoint(pos)

    def SetAbsolutePosition(self, pos):
        parent = self.parent
        if self.parent and (self.parent.type != "card" or self.GetProperty("rotation")):
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = iaff.TransformPoint(pos[0], pos[1])
        self.SetProperty("position", pos)

    def GetAbsoluteCenter(self):
        s = self.GetProperty("size")
        if self.parent and self.parent.type == "card" and not self.GetProperty("rotation"):
            pos = self.GetProperty("position")
            return pos + tuple(s/2)
        aff = self.GetAffineTransform()
        p = wx.RealPoint(*aff.TransformPoint(int(s[0]/2), int(s[1]/2)))
        return p

    def SetAbsoluteCenter(self, pos):
        parent = self.parent
        s = self.GetProperty("size")
        if not self.parent or self.parent.type == "card":
            self.SetProperty("position", pos - tuple(s/2))
        else:
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = wx.RealPoint(*iaff.TransformPoint(pos[0], pos[1])) - (int(s[0]/2), int(s[1]/2))
            self.SetProperty("position", pos)

    def IsVisible(self):
        """ Returns True iff this object or any of its ancestors has its hidden property set to True """
        if not self.properties["isVisible"]:
            return False
        if self.parent and self.parent.type not in ["card", "stack"]:
            return self.parent.IsVisible()
        return True

    def GetCenter(self):
        return self.GetProperty("center")

    def SetCenter(self, center):
        self.SetProperty("center", center)

    def GetFrame(self):
        p = self.properties["position"]
        s = self.properties["size"]
        return wx.Rect(*p, *s)

    def GetAbsoluteFrame(self):
        if self.parent and self.parent.type == "card" and not self.GetProperty("rotation"):
            return self.GetFrame()
        return self.RotatedRect(wx.Rect(wx.Point(0,0), self.properties["size"]))

    def SetFrame(self, rect):
        self.SetProperty("position", rect.Position)
        self.SetProperty("size", rect.Size)

    def GetData(self):
        handlers = {}
        for k, v in self.handlers.items():
            if len(v.strip()) > 0:
                handlers[k] = v

        props = self.properties.copy()
        props.pop("isVisible")
        props.pop("speed")
        for k,v in self.propertyTypes.items():
            if v in ["point", "floatpoint", "size"] and k in props:
                props[k] = list(props[k])
            elif v == "dict":
                props[k] = sanitizer.SanitizeDict(props[k], [])

        if len(props["data"]) == 0:
            props.pop("data")

        return {"type": self.type,
                "handlers": handlers,
                "properties": props}

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
                elif self.propertyTypes[k] == "string":
                    self.SetProperty(k, v, notify=False)
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
            if 'rotation' in keys:
                keys.remove('rotation')
            return keys
        return self.propertyKeys

    # Options currently are string, bool, int, float, point, floatpoint, size, choice, color, file
    def GetPropertyType(self, key):
        return self.propertyTypes.get(key)

    @staticmethod
    def GetPropertyChoices(key):
        if key == "alignment":
            return ["Left", "Center", "Right"]
        elif key == "font":
            return ["Default", "Serif", "Sans-Serif", "Mono"]
        elif key == "fit":
            return ["Center", "Stretch", "Contain", "Fill"]
        return []

    def GetProperty(self, key):
        if key == "center":
            return self.GetAbsoluteCenter()
        elif key in self.properties:
            return self.properties[key]
        return None

    def GetHandler(self, key):
        if key in self.handlers:
            return self.handlers[key]
        return None

    def IsAncestorOf(self, model):
        m = self
        while m.parent:
            if m == model:
                return True
            m = m.parent
        return False

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

    def PerformFlips(self, fx, fy, notify=True):
        pass

    def OrderMoveTo(self, index):
        index = index % len(self.parent.childModels) # Convert negative index to positive
        if index < 0 or index > len(self.parent.childModels)-1:
            return
        self.parent.childModels.remove(self)
        self.parent.childModels.insert(index, self)
        if self.GetCard() == self.stackManager.uiCard.model:
            ui = self.stackManager.GetUiViewByModel(self)
            if ui.view:
                self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)
            else:
                ui.parent.uiViews.remove(ui)
                ui.parent.uiViews.insert(index, ui)

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
        if self.stackManager:
            self.stackManager.OnPropertyChanged(self, key)

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        if key in self.propertyTypes and self.propertyTypes[key] == "point" and not isinstance(value, wx.Point):
            value = wx.Point(value[0], value[1])
        elif key in self.propertyTypes and self.propertyTypes[key] == "floatpoint" and not isinstance(value, wx.RealPoint):
            value = wx.RealPoint(value[0], value[1])
        elif key in self.propertyTypes and self.propertyTypes[key] == "size" and not isinstance(value, wx.Point):
            value = wx.Size(value)
        elif key in self.propertyTypes and self.propertyTypes[key] == "choice" and value not in self.GetPropertyChoices(key):
            return
        elif key in self.propertyTypes and self.propertyTypes[key] == "color" and isinstance(value, wx.Colour):
            value = value.ToHex()
        elif key in self.propertyTypes and self.propertyTypes[key] == "uint" and value < 0:
            value = 0

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
            self.SetAbsoluteCenter(value)
            return
        elif key == "rotation":
            value = value % 360

        if self.properties[key] != value:
            self.properties[key] = value
            if notify:
                self.Notify(key)
            self.isDirty = True

    def SetHandler(self, key, value):
        if self.handlers[key] != value:
            self.handlers[key] = value
            self.isDirty = True

    def SetBounceModels(self, models):
        objs = {}
        for m in models:
            if isinstance(m, ViewModel):
                objs[m] = [None, None]
        self.bounceObjs = objs

    def AddAnimation(self, key, duration, onUpdate, onStart=None, onFinish=None, onCancel=None):
        # On Runner thread
        if self.didSetDown: return
        animDict = {"duration": duration if duration != 0 else 0.01,
                    "onStart": onStart,
                    "onUpdate": onUpdate,
                    "onFinish": onFinish,
                    "onCancel": onCancel
                    }
        if key not in self.animations:
            self.animations[key] = [animDict]
            self.StartAnimation(key)
        else:
            self.animations[key].append(animDict)

    def StartAnimation(self, key):
        # On Runner or Main thread
        if key in self.animations:
            animDict = self.animations[key][0]
            if "startTime" not in animDict:
                animDict["startTime"] = time()
                if animDict["onStart"]:
                    animDict["onStart"](animDict)

    def FinishAnimation(self, key):
        # On Main thread
        if key in self.animations:
            animList = self.animations[key]
            animDict = animList[0]
            if len(animList) > 1:
                del animList[0]
                self.StartAnimation(key)
            else:
                del self.animations[key]
            if "startTime" in animDict and animDict["onFinish"]:
                animDict["onFinish"](animDict)

    def StopAnimation(self, key=None):
        # On Runner thread
        if key:
            # Stop animating this one property
            if key in self.animations:
                animDict = self.animations[key][0]
                if "startTime" in animDict and animDict["onCancel"]:
                    animDict["onCancel"](animDict)
                del self.animations[key]
            return

        # Stop animating all properties
        for (key, animList) in self.animations.items():
            animDict = animList[0]
            if "startTime" in animDict and animDict["onCancel"]:
                animDict["onCancel"](animDict)
        self.animations = {}

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

    def __repr__(self):
        return f"<{self._model.GetDisplayType()}:'{self._model.GetProperty('name')}'>"

    def __getattr__(self, item):
        model = self._model
        if model:
            for m in model.childModels:
                if m.properties["name"] == item:
                    return m.GetProxy()
        return super().__getattribute__(item)

    def SendMessage(self, message):
        if not isinstance(message, str):
            raise TypeError("SendMessage(): message must be a string")

        model = self._model
        if not model: return

        if model.stackManager.runner:
           model.stackManager.runner.RunHandler(model, "OnMessage", None, message)

    def Focus(self):
        model = self._model
        if not model: return

        if model.stackManager.runner:
            model.stackManager.runner.SetFocus(self)

    @property
    def hasFocus(self):
        model = self._model
        if not model: return False

        uiView = model.stackManager.GetUiViewByModel(model)
        if uiView and uiView.textbox:
            return model.stackManager.canvas.getActiveObject().id == uiView.textbox.id

    def Clone(self, name=None, **kwargs):
        model = self._model
        if not model: return None

        if model.type != "card":
            # update the model immediately on the runner thread
            newModel = model.CreateCopy(name)
            newModel.SetProperty("speed", model.GetProperty("speed"), notify=False)
            newModel.lastOnPeriodicTime = time()
            if not self.isVisible:
                newModel.SetProperty("isVisible", False, notify=False)
            for k,v in kwargs.items():
                if hasattr(newModel.GetProxy(), k):
                    setattr(newModel.GetProxy(), k, v)
                else:
                    raise TypeError(f"Clone(): unable to set property {k}")

            self._model.stackManager.uiCard.model.AddChild(newModel)
            newModel.RunSetup(model.stackManager.runner)
            if newModel.GetCard() != model.stackManager.uiCard.model:
                model.stackManager.runner.SetupForCard(model.stackManager.uiCard.model)

            if not newModel.didSetDown:
                # add the view on the main thread
                newModel.stackManager.AddUiViewsFromModels([newModel])
        else:
            # When cloning a card, update the model and view together in a rare synchronous call to the main thread
            newModel = model.stackManager.DuplicateCard(model)

            if "center" in kwargs and "size" in kwargs:
                newModel.SetProperty("size", kwargs["size"])
                newModel.SetProperty("center", kwargs["center"])
                kwargs.pop("size")
                kwargs.pop("center")

            for k,v in kwargs.items():
                if hasattr(newModel.GetProxy(), k):
                    setattr(newModel.GetProxy(), k, v)
                else:
                    raise TypeError(f"Clone(): unable to set property {k}")

        return newModel.GetProxy()

    def Delete(self):
        model = self._model
        if not model or not model.parent or model.parent.type == "group":
            return

        # immediately update the model
        sm = model.stackManager
        if model.type != "card":
            model.parent.RemoveChild(model)

        if model.type != "card":
            # update views on the main thread
            sm.RemoveUiViewByModel(model)
        else:
            # When cloning a card, update the model and view together in a rare synchronous call to the main thread
            sm.RemoveCardRaw(model)

    def Cut(self):
        # update the model and view together in a rare synchronous call to the main thread
        model = self._model
        if not model: return

        model.stackManager.CutModels([model], False)

    def Copy(self):
        # update the model and view together in a rare synchronous call to the main thread
        model = self._model
        if not model: return

        model.stackManager.CopyModels([model])

    # Paste is in the runner

    @property
    def name(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("name")

    @property
    def type(self):
        model = self._model
        if not model: return None
        return model.type

    @property
    def data(self):
        model = self._model
        if not model: return {}
        return model.GetProperty("data")

    @property
    def parent(self):
        model = self._model
        if not model: return None
        parent = model.parent
        if parent: parent = parent.GetProxy()
        return parent

    @property
    def children(self):
        model = self._model
        if not model: return []
        return [m.GetProxy() for m in model.childModels]

    def ChildWithBaseName(self, base):
        model = self._model
        if model and model.childModels:
            for m in model.childModels:
                if m.properties["name"].startswith(base):
                    return m.GetProxy()
        return None

    @property
    def size(self):
        model = self._model
        if not model: return wx.Size(0,0)
        return wx.CDSSize(model.GetProperty("size"), model=model, role="size")
    @size.setter
    def size(self, val):
        try:
            val = wx.Size(val[0], val[1])
        except:
            raise ValueError("size must be a size or a list of two numbers")
        model = self._model
        if not model: return
        model.SetProperty("size", val)

    @property
    def position(self):
        model = self._model
        if not model: return wx.RealPoint(0,0)
        return wx.CDSRealPoint(model.GetAbsolutePosition(), model=model, role="position")
    @position.setter
    def position(self, val):
        try:
            val = wx.RealPoint(val[0], val[1])
        except:
            raise ValueError("position must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetAbsolutePosition(val)

    @property
    def speed(self):
        model = self._model
        if not model: return wx.RealPoint(0,0)
        speed = wx.CDSRealPoint(model.GetProperty("speed"), model=model, role="speed")
        return speed
    @speed.setter
    def speed(self, val):
        try:
            val = wx.RealPoint(val[0], val[1])
        except:
            raise ValueError("speed must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetProperty("speed", val)

    @property
    def center(self):
        model = self._model
        if not model: return wx.RealPoint(0,0)
        return wx.CDSRealPoint(model.GetCenter(), model=model, role="center")
    @center.setter
    def center(self, center):
        try:
            center = wx.RealPoint(center[0], center[1])
        except:
            raise ValueError("center must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetCenter(center)

    def FlipHorizontal(self):
        model = self._model
        if not model: return
        model.PerformFlips(True, False)

    def FlipVertical(self):
        model = self._model
        if not model: return
        model.PerformFlips(False, True)

    def OrderToFront(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(-1)

    def OrderForward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(1)

    def OrderBackward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(-1)

    def OrderToBack(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(0)

    def OrderToIndex(self, i):
        if not isinstance(i, int):
            raise TypeError("OrderToIndex(): index must be a number")

        model = self._model
        if not model: return

        if i < 0 or i >= len(model.parent.childModels):
            raise TypeError("OrderToIndex(): index is out of bounds")

        if model.didSetDown: return
        model.OrderMoveTo(i)

    def Show(self):
        self.isVisible = True
    def Hide(self):
        self.isVisible = False

    @property
    def isVisible(self):
        model = self._model
        if not model: return False
        return model.IsVisible()
    @isVisible.setter
    def isVisible(self, val):
        model = self._model
        if not model: return
        model.SetProperty("isVisible", bool(val))

    @property
    def rotation(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("rotation")
    @rotation.setter
    def rotation(self, val):
        if self._model.GetProperty("rotation") is None:
            raise TypeError("object does not support rotation")
        if not isinstance(val, (int, float)):
            raise TypeError("rotation must be a number")
        model = self._model
        if not model: return
        model.SetProperty("rotation", val)

    def GetEventCode(self, eventName):
        model = self._model
        if not model: return ""
        return model.handlers[eventName]

    def SetEventCode(self, eventName, code):
        model = self._model
        if not model: return
        if not isinstance(eventName, str):
            raise TypeError("SetEventCode(): eventName must be a string")
        if not isinstance(code, str):
            raise TypeError("SetEventCode(): code must be a string")
        if eventName not in model.handlers:
            raise TypeError(f"SetEventCode(): this object has no event called '{eventName}'")

        model.handlers[eventName] = code

    def SetBounceObjects(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError("SetBounceObjects(): objects needs to be a list of cardstock objects")
        models = [o._model for o in objects if isinstance(o, ViewProxy)]
        self._model.SetBounceModels(models)

    def StopHandlingMouseEvent(self):
        self._model.stackManager.runner.StopHandlingMouseEvent()

    def IsTouchingPoint(self, point):
        if not isinstance(point, (wx.Point, wx.RealPoint, wx.CDSPoint, wx.CDSRealPoint, list, tuple)):
            raise TypeError("IsTouchingPoint(): point needs to be a point or a list of two numbers")
        if len(point) != 2:
            raise TypeError("IsTouchingPoint(): point needs to be a point or a list of two numbers")
        try:
            int(point[0]), int(point[1])
        except:
            raise ValueError("IsTouchingPoint(): point needs to be a point or a list of two numbers")

        model = self._model
        if not model: return False
        if model.didSetDown: return False
        ui = model.stackManager.GetUiViewByModel(model)
        if not ui:
            return False
        if len(ui.fabObjs) > 0:
            return ui.fabObjs[0].containsPoint(point)
        return False

    def IsTouching(self, obj):
        if not isinstance(obj, ViewProxy):
            raise TypeError("IsTouching(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel: return False

        if model.didSetDown: return False
        sUi = model.stackManager.GetUiViewByModel(model)
        oUi = model.stackManager.GetUiViewByModel(oModel)
        if not sUi or not oUi or len(sUi.fabObjs) == 0 or len(sUi.fabObjs) == 0:
            return False
        return sUi.fabObjs[0].intersectsWithObject(oUi.fabObjs[0])

    def IsTouchingEdge(self, obj, skipIsTouchingCheck=False):
        if not isinstance(obj, ViewProxy):
            raise TypeError("IsTouchingEdge(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel: return None
        ui = model.stackManager.GetUiViewByModel(model)
        # oUi = model.stackManager.GetUiViewByModel(oModel)

        if model.didSetDown or oModel.didSetDown: return None

        sFab = ui.fabObjs[0]

        # if not skipIsTouchingCheck:
        #     if not self.IsTouching(obj):
        #         return None

        rect = oModel.GetFrame() # other frame in card coords
        cornerSetback = 4
        # Pull edge lines away from the corners, so we don't always hit a corner when 2 objects touch
        rects = [wx.Rect(rect.TopLeft+(cornerSetback,0), rect.TopRight+(-cornerSetback,1)),
                  wx.Rect(rect.TopRight+(-1,cornerSetback), rect.BottomRight+(0,-cornerSetback)),
                  wx.Rect(rect.BottomLeft+(cornerSetback,-1), rect.BottomRight+(-cornerSetback,0)),
                  wx.Rect(rect.TopLeft+(0,cornerSetback), rect.BottomLeft+(1,-cornerSetback))]

        oRot = oModel.GetProperty("rotation")
        if oRot is None: oRot = 0

        # if oRot == 0:
        bottom = rects[0]
        right = rects[1]
        top = rects[2]
        left = rects[3]

        def TestRect(r):
            fabric = ui.stackManager.fabric
            r = ui.stackManager.ConvRect(r)
            tl = fabric.Point.new(r.Left, r.Top)
            br = fabric.Point.new(r.Right, r.Bottom)
            return sFab.intersectsWithRect(tl, br)

        def RotEdge(rot):
            # Rotate reported edge hits according to other object's rotation
            edgesMap = [["Top"], ["Top", "Right"], ["Right"], ["Bottom", "Right"],
                        ["Bottom"], ["Bottom", "Left"], ["Left"], ["Top", "Left"]]
            i = int(((rot+22.5)%360)/45)
            return edgesMap[i]

        edges = set()
        if TestRect(top): [edges.add(e) for e in RotEdge(oRot)]
        if TestRect(bottom): [edges.add(e) for e in RotEdge(oRot+180)]
        if TestRect(left): [edges.add(e) for e in RotEdge(oRot+270)]
        if TestRect(right): [edges.add(e) for e in RotEdge(oRot+90)]
        if len(edges) == 3 and "Top" in edges and "Bottom" in edges:
            edges.remove("Top")
            edges.remove("Bottom")
        if len(edges) == 3 and "Left" in edges and "Right" in edges:
            edges.remove("Left")
            edges.remove("Right")
        if len(edges) == 0:
            edges = None
        return edges

    def AnimatePosition(self, duration, endPosition, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimatePosition(): duration must be a number")
        try:
            endPosition = wx.RealPoint(endPosition)
        except:
            raise ValueError("AnimatePosition(): endPosition must be a point or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origPosition = model.GetAbsolutePosition()
            offsetPt = endPosition - tuple(origPosition)
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origPosition"] = origPosition
            animDict["offset"] = offset
            model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetAbsolutePosition(animDict["origPosition"] + tuple(animDict["offset"] * progress))

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def AnimateCenter(self, duration, endCenter, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateCenter(): duration must be a number")
        try:
            endCenter = wx.RealPoint(endCenter)
        except:
            raise ValueError("AnimateCenter(): endCenter must be a point or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origCenter = model.GetCenter()
            offsetPt = endCenter - tuple(origCenter)
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origCenter"] = origCenter
            animDict["offset"] = offset
            self._model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetCenter(animDict["origCenter"] + tuple(animDict["offset"] * progress))

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def AnimateSize(self, duration, endSize, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateSize(): duration must be a number")
        try:
            endSize = wx.Size(endSize)
        except:
            raise ValueError("AnimateSize(): endSize must be a size or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origSize = model.GetProperty("size")
            offset = wx.Size(endSize-tuple(origSize))
            animDict["origSize"] = origSize
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("size", animDict["origSize"] + tuple(animDict["offset"] * progress))

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("size", duration, onUpdate, onStart, internalOnFinished)

    def AnimateRotation(self, duration, endRotation, forceDirection=0, onFinished=None, *args, **kwargs):
        if self._model.GetProperty("rotation") is None:
            raise TypeError("AnimateRotation(): object does not support rotation")

        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateRotation(): duration must be a number")
        if not isinstance(endRotation, (int, float)):
            raise TypeError("AnimateRotation(): endRotation must be a number")
        if not isinstance(forceDirection, (int, float)):
            raise TypeError("AnimateRotation(): forceDirection must be a number")

        model = self._model
        if not model: return

        endRotation = endRotation

        def onStart(animDict):
            origVal = self.rotation
            animDict["origVal"] = origVal
            offset = endRotation - origVal
            if forceDirection:
                if forceDirection > 0:
                    if offset <= 0: offset += 360
                elif forceDirection < 0:
                    if offset >= 0: offset -= 360
            else:
                if offset > 180: offset -= 360
                if offset < -180: offset += 360
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("rotation", (animDict["origVal"] + animDict["offset"] * progress)%360)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("rotation", duration, onUpdate, onStart, internalOnFinished)

    def StopAnimating(self, propertyName=None):
        model = self._model
        if not model: return
        model.StopAnimation(propertyName)


class StackModel(ViewModel):
    """
    This is the model for the stack.  It mostly just contains the cards as its children.
    """

    minSize = wx.Size(200, 200)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "stack"
        self.proxyClass = Stack

        self.properties["size"] = wx.Size(500, 500)
        self.properties["name"] = "stack"
        self.properties["canSave"] = False
        self.properties["canResize"] = False

        self.propertyTypes["canSave"] = 'bool'
        self.propertyTypes["canResize"] = 'bool'

        self.propertyKeys = []

        self.handlers = {}

    def AppendCardModel(self, cardModel):
        cardModel.parent = self
        self.childModels.append(cardModel)

    def InsertCardModel(self, index, cardModel):
        cardModel.parent = self
        self.childModels.insert(index, cardModel)

    def InsertNewCard(self, name, atIndex):
        card = CardModel(self.stackManager)
        card.SetProperty("name", self.DeduplicateName(name, [m.GetProperty("name") for m in self.childModels]))
        if atIndex == -1:
            self.AppendCardModel(card)
        else:
            self.InsertCardModel(atIndex, card)
            newIndex = self.childModels.index(self.stackManager.uiCard.model)
            self.stackManager.cardIndex = newIndex
        return card

    def RemoveCardModel(self, cardModel):
        cardModel.parent = None
        self.childModels.remove(cardModel)

    def GetCardModel(self, i):
        return self.childModels[i]

    def GetModelFromPath(self, path):
        parts = path.split('.')
        m = self
        for p in parts:
            found = False
            for c in m.childModels:
                if c.properties['name'] == p:
                    m = c
                    found = True
                    break
            if not found:
                return None
        return m

    def GetData(self):
        data = super().GetData()
        data["cards"] = [m.GetData() for m in self.childModels]
        data["properties"].pop("position")
        data["properties"].pop("name")
        data["CardStock_stack_format"] = FILE_FORMAT_VERSION
        data["CardStock_stack_version"] = VERSION
        return data

    def SetData(self, stackData):
        formatVer = stackData["CardStock_stack_format"]
        if formatVer != FILE_FORMAT_VERSION:
            self.MigrateDataFromFormatVersion(formatVer, stackData)

        super().SetData(stackData)
        self.childModels = []
        for data in stackData["cards"]:
            m = CardModel(self.stackManager)
            m.parent = self
            m.SetData(data)
            self.AppendCardModel(m)

        if formatVer != FILE_FORMAT_VERSION:
            self.MigrateModelFromFormatVersion(formatVer, self)

    def MigrateDataFromFormatVersion(self, fromVer, dataDict):
        if fromVer <= 2:
            """
            In File Format Version 3, some properties and methods were renamed.
            """
            # Update names
            def replaceNames(dataDict):
                if dataDict['type'] == "poly":
                    dataDict['type'] = "polygon"
                if "bgColor" in dataDict['properties']:
                    dataDict['properties']["fillColor"] = dataDict['properties'].pop("bgColor")
                if "border" in dataDict['properties']:
                    dataDict['properties']["hasBorder"] = dataDict['properties'].pop("border")
                if "editable" in dataDict['properties']:
                    dataDict['properties']["isEditable"] = dataDict['properties'].pop("editable")
                if "multiline" in dataDict['properties']:
                    dataDict['properties']["isMultiline"] = dataDict['properties'].pop("multiline")
                if "autoShrink" in dataDict['properties']:
                    dataDict['properties']["canAutoShrink"] = dataDict['properties'].pop("autoShrink")
                if 'childModels' in dataDict:
                    for child in dataDict['childModels']:
                        replaceNames(child)
            for c in dataDict['cards']:
                replaceNames(c)

    def MigrateModelFromFormatVersion(self, fromVer, stackModel):
        if fromVer <= 1:
            """
            In File Format Version 1, the cards used the top-left corner as the origin, y increased while moving down.
            In File Format Version 2, the cards use the bottom-left corner as the origin, y increases while moving up.
            Migrate all of the static objects to look the same in the new world order, but user code will need updating.
            Also update names of the old StopAnimations() and StopAllAnimations() methods, and move OnIdle to OnPeriodic.
            """
            def UnflipImages(obj):
                if obj.type == "image":
                    obj.PerformFlips(False, True)
                else:
                    for c in obj.childModels:
                        UnflipImages(c)

            for card in stackModel.childModels:
                card.PerformFlips(False, True)
                UnflipImages(card)

            # Update names of StopAnimating methods, OnIdle->OnPeriodic
            def replaceNames(obj):
                if "OnIdle" in obj.handlers:
                    obj.handlers["OnPeriodic"] = obj.handlers.pop("OnIdle")
                for k,v in obj.handlers.items():
                    val = v
                    val = val.replace(".StopAnimations(", ".StopAnimating(")
                    val = val.replace(".StopAllAnimations(", ".StopAllAnimating(")
                    obj.handlers[k] = val
                for child in obj.childModels:
                    replaceNames(child)
            replaceNames(stackModel)
        if fromVer <= 2:
            """
            In File Format Version 3, some properties and methods were renamed.
            """
            # Update names
            def replaceNames(obj):
                for k,v in obj.handlers.items():
                    if len(v):
                        val = v
                        val = val.replace(".bgColor", ".fillColor")
                        val = val.replace(".AnimateBgColor(", ".AnimateFillColor(")
                        val = val.replace(".border", ".hasBorder")
                        val = val.replace(".editable", ".isEditable")
                        val = val.replace(".multiline", ".isMultiline")
                        val = val.replace(".autoShrink", ".canAutoShrink")
                        val = val.replace(".visible", ".isVisible")
                        val = val.replace(".GetEventHandler(", ".GetEventCode(")
                        val = val.replace(".SetEventHandler(", ".SetEventCode(")
                        obj.handlers[k] = val
                for child in obj.childModels:
                    replaceNames(child)
            replaceNames(stackModel)


class Stack(ViewProxy):
    @property
    def numCards(self):
        return len(self._model.childModels)

    @property
    def currentCard(self):
        if self._model.didSetDown: return None
        return self._model.stackManager.uiCard.model.GetProxy()

    def CardWithNumber(self, number):
        model = self._model
        if model.didSetDown: return None
        if not isinstance(number, int):
            raise TypeError("CardWithNumber(): number is not an int")
        if number < 1 or number > len(model.childModels):
            raise ValueError("CardWithNumber(): number is out of bounds")
        return model.childModels[number-1].GetProxy()

    def Return(self, result=None):
        self._model.stackManager.runner.ReturnFromStack(result)

    def GetSetupValue(self):
        return self._model.stackManager.runner.GetStackSetupValue()

    def AddCard(self, name="card", atNumber=0):
        if not isinstance(name, str):
            raise TypeError("AddCard(): name is not a string")
        atNumber = int(atNumber)
        if atNumber < 0 or atNumber > len(self._model.childModels)+1:
            raise ValueError("AddCard(): atNumber is out of bounds")

        if self._model.didSetDown: return None
        return self._model.InsertNewCard(name, atNumber-1).GetProxy()


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
        handlers = {"OnSetup": "", "OnShowCard": "", "OnKeyDown": "", "OnKeyHold": "", "OnKeyUp": ""}
        del self.handlers["OnBounce"]
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.handlers["OnResize"] = ""
        self.handlers["OnHideCard"] = ""
        self.handlers["OnExitStack"] = ""
        self.initialEditHandler = "OnSetup"

        # Custom property order and mask for the inspector
        self.properties["name"] = "card_1"
        self.properties["fillColor"] = "white"
        self.propertyKeys = ["name", "fillColor", "size", "canSave", "canResize"]

        self.propertyTypes["fillColor"] = "color"
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
            m = self.stackManager.ModelFromData(self.stackManager, childData)
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
        model = self.stackManager.ModelFromType(self.stackManager, typeStr)
        model.SetProperty("name", name, notify=False)
        self.DeduplicateNamesForModels([model])
        if size:
            model.SetProperty("size", size, notify=False)
        if isinstance(model, LineModel):
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

        # add the view on the main thread
        if self.didSetDown: return
        if self.stackManager.uiCard.model == self:
            self.stackManager.AddUiViewsFromModels([model])

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
    def fillColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fillColor")
    @fillColor.setter
    def fillColor(self, val):
        if not isinstance(val, str):
            raise TypeError("fillColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fillColor", val)

    @property
    def number(self):
        model = self._model
        if not model: return -1
        return model.parent.childModels.index(model)+1

    def AnimateFillColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateFillColor(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("AnimateFillColor(): endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.fillColor)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("fillColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("fillColor", duration, onUpdate, onStart, internalOnFinished)

    def AddButton(self, name="button", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("button", name, (100,24), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddTextField(self, name="field", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("textfield", name, (100,24), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddTextLabel(self, name="label", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("textlabel", name, (100,24), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddImage(self, name="image", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("image", name, (80,80), kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddOval(self, name="oval", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("oval", name, None, [(10, 10), (100, 100)], kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddRectangle(self, name="rect", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("rect", name, None, [(10, 10), (100, 100)], kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddRoundRectangle(self, name="roundrect", **kwargs):
        model = self._model
        if not model: return None
        obj = model.AddNewObject("roundrect", name, None, [(10, 10), (100, 100)], kwargs=kwargs)
        return obj.GetProxy() if obj else None

    def AddLine(self, points, name="line", **kwargs):
        if not isinstance(points, (list, tuple)):
            raise TypeError("AddLine(): points should be a list of points")
        if len(points) < 2:
            raise TypeError("AddLine(): points should be a list of at least 2 points")
        for p in points:
            if not isinstance(p, (wx.Point, wx.RealPoint, wx.CDSPoint, wx.CDSRealPoint, list, tuple)):
                raise TypeError("AddLine(): points items each need to be a point or a list of two numbers")
            if len(p) != 2:
                raise TypeError("AddLine(): points items each need to be a point or a list of two numbers")
            try:
                int(p[0]), int(p[1])
            except:
                raise ValueError("AddLine(): points items each need to be a point or a list of two numbers")

        model = self._model
        if not model: return None

        line = model.AddNewObject("line", name, None, points, kwargs=kwargs)
        return line.GetProxy() if line else None

    def AddPolygon(self, points, name="polygon", **kwargs):
        if not isinstance(points, (list, tuple)):
            raise TypeError("AddPolygon(): points should be a list of points")
        if len(points) < 2:
            raise TypeError("AddPolygon(): points should be a list of at least 2 points")
        for p in points:
            if not isinstance(p, (wx.Point, wx.RealPoint, wx.CDSPoint, wx.CDSRealPoint, list, tuple)):
                raise TypeError("AddPolygon(): points items each need to be a point or a list of two numbers")
            if len(p) != 2:
                raise TypeError("AddPolygon(): points items each need to be a point or a list of two numbers")
            try:
                int(p[0]), int(p[1])
            except:
                raise ValueError("AddPolygon(): points items each need to be a point or a list of two numbers")

        model = self._model
        if not model: return None

        poly = model.AddNewObject("polygon", name, None, points, kwargs=kwargs)
        return poly.GetProxy() if poly else None

    def AddGroup(self, objects, name="group"):
        models = []
        for o in objects:
            if not isinstance(o, ViewProxy):
                raise TypeError("AddGroup(): objects must be a list of objects")
            if o._model.type not in ["card", "stack"] and o._model.GetCard() == self._model:
                models.append(o._model)

        model = self._model
        if not model: return None

        if model.didSetDown: return None
        g = model.stackManager.GroupModelsInternal(models, name=name)
        return g.GetProxy() if g else None

    def StopAllAnimating(self, propertyName=None):
        model = self._model
        if not model: return
        model.StopAnimation(propertyName)
        for child in model.GetAllChildModels():
            child.StopAnimation(propertyName)


class ButtonModel(ViewModel):
    """
    This is the model for a Button object.
    """

    minSize = wx.Size(34,20)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "button"
        self.proxyClass = Button

        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "",
                    "OnClick": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnClick"

        self.properties["name"] = "button_1"
        self.properties["title"] = "Button"
        self.properties["hasBorder"] = True
        self.propertyTypes["title"] = "string"
        self.propertyTypes["hasBorder"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "title", "hasBorder", "position", "size"]


class Button(ViewProxy):
    """
    Button proxy objects are the user-accessible objects exposed to event handler code for button objects.
    Based on ProxyView, and adds title, border, and Click().
    """

    @property
    def title(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("title")
    @title.setter
    def title(self, val):
        model = self._model
        if not model: return
        model.SetProperty("title", str(val))

    @property
    def hasBorder(self):
        model = self._model
        if not model: return False
        return model.GetProperty("hasBorder")
    @hasBorder.setter
    def hasBorder(self, val):
        model = self._model
        if not model: return
        model.SetProperty("hasBorder", bool(val))

    def Click(self):
        model = self._model
        if not model: return
        if model.stackManager.runner and model.GetHandler("OnClick"):
            model.stackManager.runner.RunHandler(model, "OnClick", None)


class TextBaseModel(ViewModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.proxyClass = None

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["textColor"] = "black"
        self.properties["font"] = "Default"
        self.properties["fontSize"] = 18

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["textColor"] = "color"
        self.propertyTypes["font"] = "choice"
        self.propertyTypes["fontSize"] = "uint"


class TextBaseProxy(ViewProxy):
    """
    TextBaseProxy objects are the abstract base class of the user-accessible objects exposed to event handler code for
    text labels and text fields.
    """

    @property
    def text(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("text")
    @text.setter
    def text(self, val):
        model = self._model
        if not model: return
        model.SetProperty("text", str(val))

    @property
    def alignment(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("alignment")
    @alignment.setter
    def alignment(self, val):
        if not isinstance(val, str):
            raise TypeError("alignment must be a string")
        model = self._model
        if not model: return
        model.SetProperty("alignment", val)

    @property
    def textColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("textColor")
    @textColor.setter
    def textColor(self, val):
        if not isinstance(val, str):
            raise TypeError("textColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("textColor", val)

    @property
    def font(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("font")
    @font.setter
    def font(self, val):
        if not isinstance(val, str):
            raise TypeError("font must be a string")
        model = self._model
        if not model: return
        model.SetProperty("font", val)

    @property
    def fontSize(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("fontSize")
    @fontSize.setter
    def fontSize(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("fontSize must be a number")
        model = self._model
        if not model: return
        model.SetProperty("fontSize", val)

    def AnimateTextColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateTextColor(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("AnimateTextColor(): endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.textColor)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("textColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("textColor", duration, onUpdate, onStart, internalOnFinished)


class TextLabelModel(TextBaseModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textlabel"
        self.proxyClass = TextLabel
        self.properties["name"] = "label_1"
        self.properties["canAutoShrink"] = True
        self.properties["rotation"] = 0.0

        self.propertyTypes["canAutoShrink"] = "bool"
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "canAutoShrink", "position", "size", "rotation"]


class TextLabel(TextBaseProxy):
    """
    TextLabel proxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    @property
    def canAutoShrink(self):
        model = self._model
        if not model: return False
        return model.GetProperty("canAutoShrink")
    @canAutoShrink.setter
    def canAutoShrink(self, val):
        model = self._model
        if not model: return
        model.SetProperty("canAutoShrink", bool(val))


class TextFieldModel(TextBaseModel):
    """
    This is the model for a TextField object.
    """

    minSize = wx.Size(32,20)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textfield"
        self.proxyClass = TextField

        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "", "OnTextChanged": "", "OnTextEnter": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnTextEnter"

        self.properties["name"] = "field_1"
        self.properties["isEditable"] = True
        self.properties["isMultiline"] = False
        self.properties["fontSize"] = 12

        self.propertyTypes["isEditable"] = "bool"
        self.propertyTypes["isMultiline"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "isEditable", "isMultiline", "position", "size"]

    def GetSelectedText(self):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.textbox:
            return uiView.textbox.text[uiView.textbox.selectionStart:uiView.textbox.selectionEnd]
        else:
            return ""

    def SetSelectedText(self, text):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.textbox:
            text = uiView.textbox.text
            uiView.textbox.set({'text': text[:uiView.textbox.selectionStart] + text + text[uiView.textbox.selectionEnd:]})

    def GetSelection(self):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.textbox:
            return (uiView.textbox.selectionStart, uiView.textbox.selectionEnd)
        return (0,0)

    def SetSelection(self, start_index, end_index):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.textbox:
            uiView.textbox.set({'selectionStart': start_index, 'selectionEnd':end_index})


class TextField(TextBaseProxy):
    """
    TextField proxy objects are the user-accessible objects exposed to event handler code for text field objects.
    """

    @property
    def isEditable(self):
        model = self._model
        if not model: return False
        return model.GetProperty("isEditable")
    @isEditable.setter
    def isEditable(self, val):
        model = self._model
        if not model: return
        model.SetProperty("isEditable", bool(val))

    @property
    def isMultiline(self):
        model = self._model
        if not model: return False
        return model.GetProperty("isMultiline")
    @isMultiline.setter
    def isMultiline(self, val):
        model = self._model
        if not model: return
        model.SetProperty("isMultiline", bool(val))

    @property
    def selection(self):
        model = self._model
        if not model: return False
        return model.GetSelection()
    @selection.setter
    def selection(self, val):
        model = self._model
        if not model: return
        if isinstance(val, (list, tuple)) and len(val) == 2:
            if isinstance(val[0], int) and isinstance(val[1], int):
                model.SetSelection(val[0], val[1])
                return
        raise TypeError("selection must be a list of 2 numbers (start_position, end_position)")

    @property
    def selectedText(self):
        model = self._model
        if not model: return False
        return model.GetSelectedText()
    @selectedText.setter
    def selectedText(self, val):
        model = self._model
        if not model: return
        if isinstance(val,str):
            model.SetSelectedText(val)
            return
        raise TypeError("selectedText must be a string")

    def SelectAll(self):
        model = self._model
        if not model: return
        model.Notify("selectAll")

    def Enter(self):
        model = self._model
        if not model: return
        if model.didSetDown: return
        model.stackManager.runner.RunHandler(model, "OnTextEnter", None)


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
            model = self.stackManager.ModelFromData(self.stackManager, childData)
            model.parent = self
            self.childModels.append(model)
            model.origGroupSubviewFrame = model.GetFrame()
            model.origGroupSubviewRotation = model.GetProperty("rotation")
        self.origFrame = self.GetFrame()

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        super().SetProperty(key, value, notify)
        if key == "isVisible":
            for m in self.GetAllChildModels():
                m.Notify("isVisible")

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
                    m.origGroupSubviewRotation = -m.origGroupSubviewRotation
                pos = m.origGroupSubviewFrame.Position
                size = m.origGroupSubviewFrame.Size
                pos = wx.Point((self.origFrame.Size.width - (pos.x + size.width)) if fx else pos.x,
                               (self.origFrame.Size.height - (pos.y + size.height)) if fy else pos.y)
                m.origGroupSubviewFrame.Position = pos
            for m in self.childModels:
                m.PerformFlips(fx, fy, notify=notify)
                if fx != fy:
                    m.SetProperty("rotation", -m.GetProperty("rotation"))
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
            if oldRot == 0:
                # If this child is not rotated, just scale it
                m.SetFrame(wx.Rect((pos.x*scaleX, pos.y*scaleY), (size.Width*scaleX, size.Height*scaleY)))
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
                center = wx.Point((points[0].x + points[1].x + points[2].x + points[3].x) / 4,
                                  (points[0].y + points[1].y + points[2].y + points[3].y) / 4)
                if size.Height > size.Width:
                    # if the height is longer, scale the width to get thinner as the parallelogram folds up
                    size = wx.Size(math.cos(math.radians(rotB-rotA)) * math.sqrt((points[0].x - points[1].x)**2 + (points[0].y - points[1].y)**2),
                                   math.sqrt((points[1].x - points[2].x) ** 2 + (points[1].y - points[2].y) ** 2))
                else:
                    # if the width is longer, scale the height to get thinner as the parallelogram folds up
                    size = wx.Size(math.sqrt((points[0].x - points[1].x) ** 2 + (points[0].y - points[1].y) ** 2),
                                   math.cos(math.radians(rotB-rotA)) * math.sqrt((points[1].x - points[2].x) ** 2 + (points[1].y - points[2].y) ** 2))
                m.SetFrame(wx.Rect(center - tuple(size/2), size))


class Group(ViewProxy):
    """
    Group proxy objects are the user-accessible objects exposed to event handler code for group objects.
    """

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


class ImageModel(ViewModel):
    """
    This is the model for an Image object.
    """

    minSize = wx.Size(2, 2)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "image"
        self.proxyClass = Image

        self.properties["name"] = "image_1"
        self.properties["file"] = ""
        self.properties["fit"] = "Contain"
        self.properties["rotation"] = 0.0
        self.properties["xFlipped"] = False
        self.properties["yFlipped"] = False

        self.propertyTypes["file"] = "file"
        self.propertyTypes["fit"] = "choice"
        self.propertyTypes["rotation"] = "float"
        self.propertyTypes["xFlipped"] = "bool"
        self.propertyTypes["yFlipped"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "fit", "position", "size", "rotation"]

    def PerformFlips(self, fx, fy, notify=True):
        super().PerformFlips(fx, fy, notify)
        if fx:
            self.SetProperty("xFlipped", not self.GetProperty("xFlipped"), notify=notify)
        if fy:
            self.SetProperty("yFlipped", not self.GetProperty("yFlipped"), notify=notify)


class Image(ViewProxy):
    """
    Image proxy objects are the user-accessible objects exposed to event handler code for image objects.
    """

    @property
    def file(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("file")
    @file.setter
    def file(self, val):
        if not isinstance(val, str):
            raise TypeError("file must be a string")
        model = self._model
        if not model: return
        model.SetProperty("file", val)

    @property
    def fit(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fit")
    @fit.setter
    def fit(self, val):
        if not isinstance(val, str):
            raise TypeError("fit must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fit", val)


class WebViewModel(ViewModel):
    """
    This is the model for a WebView object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "webview"
        self.proxyClass = WebView

        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "", "OnDoneLoading": "", "OnCardStockLink": ""}
        for k,v in self.handlers.items():
            if "Mouse" not in k:
                handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnDoneLoading"

        self.properties["name"] = "webview_1"
        self.properties["URL"] = ""
        self.properties["HTML"] = ""
        self.properties["allowedHosts"] = []
        self.propertyTypes["URL"] = "string"
        self.propertyTypes["HTML"] = "string"
        self.propertyTypes["allowedHosts"] = "list"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "URL", "allowedHosts", "position", "size"]

    def SetProperty(self, key, value, notify=True):
        if key == "URL":
            if len(value):
                parts = urlparse(value)
                if not parts.scheme:
                    value = "https://" + value
        elif key == "allowedHosts":
            if isinstance(value, (list, tuple)):
                value = [str(i) for i in value]
        super().SetProperty(key, value, notify)


class WebView(ViewProxy):
    """
    WebView proxy objects are the user-accessible objects exposed to event handler code for WebView objects.
    """

    @property
    def URL(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("URL")
    @URL.setter
    def URL(self, val):
        if not isinstance(val, str):
            raise TypeError("URL must be set to a string value")
        model = self._model
        if not model: return
        model.SetProperty("HTML", "", notify=False)
        model.SetProperty("URL", str(val))

    @property
    def HTML(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("HTML")
    @HTML.setter
    def HTML(self, val):
        if not isinstance(val, str):
            raise TypeError("HTML must be set to a string value")
        model = self._model
        if not model: return
        model.SetProperty("URL", "", notify=False)
        model.SetProperty("HTML", str(val))

    @property
    def allowedHosts(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("allowedHosts")
    @allowedHosts.setter
    def allowedHosts(self, val):
        if not isinstance(val, (list, tuple)):
            raise TypeError("allowedHosts must be set to a list value")
        model = self._model
        if not model: return
        model.SetProperty("allowedHosts", val)

    @property
    def canGoBack(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.webView.CanGoBack()
        return False

    @property
    def canGoForward(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.webView.CanGoForward()
        return False

    def GoBack(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            ui.webView.GoBack()

    def GoForward(self):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            ui.webView.GoForward()

    def RunJavaScript(self, code):
        ui = self._model.stackManager.GetUiViewByModel(self._model)
        if ui:
            return ui.RunJavaScript(code)
        return None


class LineModel(ViewModel):
    """
    This is the model class for Line and Pen objects, and the superclass for models for the other shapes.
    """

    minSize = wx.Size(2, 2)

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager)
        self.type = shapeType
        self.proxyClass = Line
        self.points = []
        self.scaledPoints = None

        if shapeType == "pen":
            self.properties["name"] = "line_1"
        elif shapeType == "polygon":
            self.properties["name"] = "polygon_1"
        else:
            self.properties["name"] = f"{shapeType}_1"

        self.properties["originalSize"] = None
        self.properties["penColor"] = "black"
        self.properties["penThickness"] = 2
        self.properties["rotation"] = 0.0

        self.propertyTypes["originalSize"] = "size"
        self.propertyTypes["penColor"] = "color"
        self.propertyTypes["penThickness"] = "uint"
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "position", "size", "rotation"]

    def GetData(self):
        data = super().GetData()
        data["points"] = self.points.copy()
        return data

    def SetData(self, data):
        super().SetData(data)
        self.type = data["type"]
        self.points = data["points"]

    def SetShape(self, shape):
        self.type = shape["type"]
        self.properties["penColor"] = shape["penColor"]
        self.properties["penThickness"] = shape["thickness"]
        self.points = shape["points"]
        self.isDirty = True
        self.Notify("shape")

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        if key == "size":
            self.scaledPoints = None
        super().SetProperty(key, value, notify)

    def DidUpdateShape(self):  # If client updates the points list already passed to AddShape
        self.isDirty = True
        self.scaledPoints = None
        self.Notify("shape")

    def PerformFlips(self, fx, fy, notify=True):
        super().PerformFlips(fx, fy, notify)
        if self.type in ["line", "pen", "polygon"]:
            if fx or fy:
                origSize = self.properties["originalSize"]
                self.points = [((origSize[0] - p[0]) if fx else p[0], (origSize[1] - p[1]) if fy else p[1]) for p in self.points]
                self.scaledPoints = None
                if notify:
                    self.Notify("size")


    # scale from originalSize to Size
    # take into account thickness/2 border on each side
    def GetScaledPoints(self):
        if self.scaledPoints:
            return self.scaledPoints

        origSize = self.properties["originalSize"]
        size = self.GetProperty("size")

        if not origSize or origSize[0] == 0 or origSize[1] == 0:
            return self.points
        scaleX = 1
        scaleY = 1
        if origSize[0] != 0:
            scaleX = size[0] / origSize[0]
        if origSize[1] != 0:
            scaleY = size[1] / origSize[1]
        points = [(p[0] * scaleX, p[1] * scaleY) for p in self.points]
        self.scaledPoints = points
        return self.scaledPoints

    def GetAbsolutePoints(self):
        pos = self.GetAbsolutePosition()
        return [p + pos for p in self.GetScaledPoints()]

    @staticmethod
    def RectFromPoints(points):
        rect = wx.Rect(points[0][0], points[0][1], 1, 1)
        for x, y in points[1:]:
            if x < rect.Left:
                rect.Left = x
            elif x > rect.Left + rect.Width:
                rect.Width = x - rect.Left
            if y < rect.Top:
                rect.Top = y
            elif y > rect.Top + rect.Height:
                rect.Height = y - rect.Top
        return rect

    # Re-fit the bounding box to the shape
    def ReCropShape(self):
        if len(self.points) == 0:
            return

        oldSize = self.GetProperty("size") if self.properties["originalSize"] else None

        # First move all points to be relative to the card origin
        offset = self.GetProperty("position")
        points = self.points.copy()
        # adjust all points in shape
        i = 0
        for x, y in points:
            points[i] = (x + offset[0], y + offset[1])
            i += 1

        if len(points) > 0:
            rect = self.RectFromPoints(points)
        else:
            return

        # adjust view rect
        self.SetProperty("position", rect.Position)
        if rect.Width < self.minSize.width: rect.Width = self.minSize.width
        if rect.Height < self.minSize.height: rect.Height = self.minSize.height

        if oldSize:
            self.SetProperty("size", [oldSize[0], oldSize[1]])
        else:
            self.SetProperty("size", rect.Size)
        self.SetProperty("originalSize", rect.Size)

        if len(points) > 0:
            # adjust all points in shape
            i = 0
            for x,y in points:
                points[i] = (x-rect.Left, y-rect.Top)
                i += 1

        self.points = points
        self.DidUpdateShape()

    def SetPoints(self, points):
        cardSize = self.GetCard().GetProperty("size")
        self.SetProperty("position", (0,0), notify=False)
        self.SetProperty("size", cardSize, notify=False)
        self.properties["originalSize"] = None
        self.points = points
        self.ReCropShape()


class Line(ViewProxy):
    """
    Line proxy objects are the user-accessible objects exposed to event handler code for line objects.
    """

    @property
    def penColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("penColor")
    @penColor.setter
    def penColor(self, val):
        if not isinstance(val, str):
            raise TypeError("penColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("penColor", val)

    @property
    def penThickness(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("penThickness")
    @penThickness.setter
    def penThickness(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("penThickness must be a number")
        model = self._model
        if not model: return
        model.SetProperty("penThickness", val)

    @property
    def points(self):
        model = self._model
        if not model or not model.parent: return []
        return model.GetAbsolutePoints()
    @points.setter
    def points(self, points):
        model = self._model
        if not model or not model.parent: return

        try:
            points = [wx.RealPoint(p[0], p[1]) for p in points]
        except:
            raise ValueError("points must be either a list of points, or a list of lists of two numbers")

        model.SetPoints(points)

    def AnimatePenThickness(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimatePenThickness(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("AnimatePenThickness(): endThickness must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.penThickness
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("penThickness", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("penThickness", duration, onUpdate, onStart, internalOnFinished)

    def AnimatePenColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimatePenColor(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("AnimatePenColor(): endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.penColor)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("penColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("penColor", duration, onUpdate, onStart, internalOnFinished)


class ShapeModel(LineModel):
    """
    This is the model class for Oval and Rectangle objects, and the superclass for models for round-rects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = Shape

        self.properties["fillColor"] = "white"
        self.propertyTypes["fillColor"] = "color"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "fillColor", "position", "size", "rotation"]

    def SetShape(self, shape):
        self.properties["fillColor"] = shape["fillColor"]
        super().SetShape(shape)


class Shape(Line):
    """
    Shape proxy objects are the user-accessible objects exposed to event handler code for oval and rect objects.
    They're extended from the Line proxy class.
    """

    @property
    def points(self):
        model = self._model
        if model and model.parent:
            if model.type == "polygon":
                return model.GetAbsolutePoints()
            else:
                raise TypeError(f"The points property is not available for shapes of type {model.type}.")
    @points.setter
    def points(self, points):
        model = self._model
        if model and model.parent:
            if model.type == "polygon":
                try:
                    points = [wx.RealPoint(p[0], p[1]) for p in points]
                except:
                    raise ValueError("points must be either a list of points, or a list of lists of two numbers")
                model.SetPoints(points)
            else:
                raise TypeError(f"The points property is not available for shapes of type {model.type}.")

    @property
    def fillColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fillColor")
    @fillColor.setter
    def fillColor(self, val):
        if not isinstance(val, str):
            raise TypeError("fillColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fillColor", val)

    def AnimateFillColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateFillColor(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("AnimateFillColor(): endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.fillColor)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("fillColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("fillColor", duration, onUpdate, onStart, internalOnFinished)


class RoundRectModel(ShapeModel):
    """
    This is the model class for Round Rectangle objects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = RoundRect

        self.properties["cornerRadius"] = 8
        self.propertyTypes["cornerRadius"] = "uint"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "fillColor", "cornerRadius", "position", "size", "rotation"]

    def SetShape(self, shape):
        self.properties["cornerRadius"] = shape["cornerRadius"] if "cornerRadius" in shape else 8
        super().SetShape(shape)


class RoundRect(Shape):
    """
    RoundRect proxy objects are the user-accessible objects exposed to event handler code for round rect objects.
    They're extended from ShapeProxy, which is extended from the Line proxy class.
    """

    @property
    def cornerRadius(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("cornerRadius")
    @cornerRadius.setter
    def cornerRadius(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("cornerRadius must be a number")
        model = self._model
        if not model: return
        model.SetProperty("cornerRadius", val)

    def AnimateCornerRadius(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateCornerRadius(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("AnimateCornerRadius(): endCornerRadius must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.cornerRadius
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("cornerRadius", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("cornerRadius", duration, onUpdate, onStart, internalOnFinished)
