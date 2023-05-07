# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

try:
    from browser import window as context
except:
    from browser import self as context

import wx_compat as wx
import sanitizer
from urllib.parse import urlparse
import math
import migrations
from time import time
import re

VERSION='0.99.2'
FILE_FORMAT_VERSION=6


class ViewModel(object):
    """
    This is the abstract base class for the other model classes.
    The model holds the property values and event handler text for each object.
    It also holds the type of each property, and the ordered list of properties to display in the inspector.
    It also handles animating properties of the object, like position, size, or color.
    """

    minSize = wx.Size(20, 20)
    reservedNames = ['key_name', 'mouse_pos', 'message', 'URL', 'did_load', 'other_object', 'edge', 'elapsed_time', 'self',
                     'stack', 'card', 'wait', 'distance', 'run_after_delay', 'time', 'paste', 'alert', 'ask_yes_no',
                     'ask_text', 'goto_card', 'goto_next_card', 'goto_previous_card', 'run_stack', 'play_sound', 'stop_sound',
                     'broadcast_message', 'is_key_pressed', 'is_mouse_pressed', 'get_mouse_pos', 'Color', 'Point', 'Size', 'quit',
                     'name', 'type', 'data', 'position', 'size', 'center', 'rotation', 'speed', 'is_visible', 'has_focus',
                     'parent', 'children', 'copy', 'cut', 'clone', 'delete', 'send_message', 'focus', 'show', 'hide',
                     'child_with_base_name', 'flip_horizontal', 'flip_vertical', 'order_to_front', 'order_forward',
                     'order_backward', 'order_to_back', 'order_to_index', 'get_event_code', 'set_event_code',
                     'stop_handling_mouse_event', 'is_touching', 'set_bounce_objects', 'is_touching_point', 'is_touching_edge',
                     'animate_position', 'animate_center', 'animate_size', 'animate_rotation', 'stop_animating', 'fill_color',
                     'number', 'can_save', 'can_resize', 'add_button', 'add_text_field', 'AddTextLabel', 'add_image', 'add_oval',
                     'add_rectangle', 'add_round_rectangle', 'add_line', 'add_polygon', 'add_group', 'animate_fill_color',
                     'stop_all_animating', 'num_cards', 'current_card', 'False', 'None', 'True', '__peg_parser__', 'and',
                     'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
                     'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
                     'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']

    def __init__(self, stackManager):
        super().__init__()
        self.type = None
        self.parent = None
        self.handlers = {"on_setup": "",
                         "on_mouse_enter": "",
                         "on_mouse_press": "",
                         "on_mouse_move": "",
                         "on_mouse_release": "",
                         "on_mouse_exit": "",
                         "on_bounce": "",
                         "on_message": "",
                         "on_periodic": ""
                         }
        self.initialEditHandler = "on_mouse_press"
        self.visibleHandlers = set()

        self.properties = {"name": "",
                           "size": wx.Size(0,0),
                           "position": wx.RealPoint(0,0),
                           "speed": wx.Point(0,0),
                           "is_visible": True,
                           "data": {}
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "floatpoint",
                              "center": "floatpoint",
                              "size": "size",
                              "speed": "point",
                              "is_visible": "bool",
                              "data": "dict"
                              }

        self.childModels = []
        self.stackManager = stackManager
        self.isDirty = False
        self.proxy = None
        self.lastOnPeriodicTime = None
        self.animations = {}
        self.bounceObjs = {}
        self.polygons = []
        self.isPolyDirty = False
        self.polygonPos = None
        self.isPolyRect = True

        self.proxyClass = ViewProxy
        self.didSetDown = False
        self.clonedFrom = None

    def __repr__(self):
        return f"<{self.GetDisplayType()}:'{self.GetProperty('name')}'>"

    def SetBackUp(self, stackManager):
        if self in stackManager.delayedSetDowns:
            stackManager.delayedSetDowns.remove(self)
        else:
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
        self.polygons = None
        self.polygonPos = None
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

    def GetDisplayType(self):
        return self.displayTypes[self.type]

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

    def GetPath(self, subName=None):
        parts = []
        if subName:
            parts.append(subName)
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
            pos = m.properties["position"]
            size = m.properties["size"]
            rot = m.properties.get("rotation")
            aff.Translate(*(pos + (int(size[0]/2), int(size[1]/2))))
            if rot:
                aff.Rotate(math.radians(-rot))
            aff.Translate(-int(size[0]/2), -int(size[1]/2))
        return aff

    def RotatedPoints(self, points, aff=None):
        # convert points in the local system to abs
        if aff is None:
            aff = self.GetAffineTransform()
        rotPts = [wx.RealPoint(aff.TransformPoint(*p)) for p in points]
        return rotPts

    def RotatedRectPoints(self, rect, aff=None):
        # Convert local rect to absolute corner points
        points = [rect.BottomLeft, rect.BottomRight, rect.TopRight, rect.TopLeft]
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
        rot = self.properties.get("rotation")
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

    def GetAbsoluteRotation(self):
        rot = 0
        m = self
        while m and m.type not in ("card", "stack"):
            r = m.GetProperty('rotation')
            if r: rot += r
            m = m.parent
        return rot

    def GetAbsolutePosition(self):
        parent = self.parent
        pos = self.properties["position"]
        if self.parent and self.parent.type != "card":
            aff = parent.GetAffineTransform()
            pos = aff.TransformPoint(*pos)
            return wx.RealPoint(pos)
        return pos

    def SetAbsolutePosition(self, pos):
        parent = self.parent
        if self.parent and self.parent.type != "card":
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = iaff.TransformPoint(pos[0], pos[1])
        self.SetProperty("position", pos)

    def GetAbsoluteCenter(self):
        s = self.GetProperty("size")
        if self.parent and self.parent.type == "card":
            pos = self.properties["position"]
            return pos + (s[0]/2, s[1]/2)
        aff = self.GetAffineTransform()
        p = wx.RealPoint(*aff.TransformPoint(int(s[0]/2), int(s[1]/2)))
        return p

    def SetAbsoluteCenter(self, pos):
        parent = self.parent
        s = self.GetProperty("size")
        if not self.parent or self.parent.type == "card":
            self.SetProperty("position", pos - (s[0]/2, s[1]/2))
        else:
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = wx.RealPoint(*iaff.TransformPoint(pos[0], pos[1])) - (int(s[0]/2), int(s[1]/2))
            self.SetProperty("position", pos)

    def IsVisible(self):
        """ Returns False iff this object or any of its ancestors has its is_visible property set to False """
        if not self.properties["is_visible"]:
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
        if self.parent and self.parent.type == "card" and not self.properties.get("rotation"):
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

        props = {k:v for k,v in self.properties.items() if v is not None}
        props.pop("is_visible")
        props.pop("speed")
        for k,v in self.propertyTypes.items():
            if v in ["point", "floatpoint", "size"] and k in props:
                props[k] = [int(props[k][0]), int(props[k][1])]
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
            if k in self.propertyTypes and v is not None:
                if self.propertyTypes[k] == "point":
                    self.SetProperty(k, wx.Point(v), notify=False)
                elif self.propertyTypes[k] == "floatpoint":
                    self.SetProperty(k, wx.RealPoint(int(float(v[0])), int(float(v[1]))), notify=False)
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
        elif key == "style":
            return ["Border", "Borderless", "Checkbox", "Radio"]
        return []

    def GetProperty(self, key):
        if key == "center":
            return self.GetAbsoluteCenter()
        elif key == "is_visible":
            return self.IsVisible()
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
        card = self.GetCard()
        if card == self.stackManager.uiCard.model:
            ui = self.stackManager.GetUiViewByModel(self)
            ui.parent.uiViews.remove(ui)
            ui.parent.uiViews.insert(index, ui)
            n = self.stackManager.uiCard.GetFirstFabIndexForUiView(ui)
            if n is None:
                return
            for fabId in ui.fabIds:
                context.stackWorker.SendAsync(("fabReorder", fabId, n))
                n += 1

    def OrderMoveBy(self, delta):
        index = self.parent.childModels.index(self)
        if (delta < 0 and index > 0) or (delta > 0 and index < len(self.parent.childModels)-1):
            index += delta
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
        elif key in self.propertyTypes and self.propertyTypes[key] == "size" and not isinstance(value, wx.Size):
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
            if key in ("rotation", "size"):
                self.polygons = []
            if key == "position":
                self.isPolyDirty = True
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

    def GetPolygons(self):
        if not self.polygons:
            self.MakePolygon()
            self.polygonPos = wx.Point(self.properties['position'])
        elif self.isPolyDirty:
            self.MovePolygon()
        return self.polygons

    def MakePolygon(self):
        s = self.GetProperty('size')
        f = wx.Rect(0, 0, s[0], s[1])
        points = self.RotatedRectPoints(f)
        self.polygons = [context.SAT.Polygon.new(context.SAT.Vector.new(),
                                              [context.SAT.Vector.new(p.x, p.y) for p in points])]

    def MovePolygon(self):
        if self.polygons:
            newPos = self.GetAbsolutePosition()
            dx,dy = (newPos[0] - self.polygonPos[0], newPos[1] - self.polygonPos[1])
            for poly in self.polygons:
                poly.setOffset(context.SAT.Vector.new(dx, dy))

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
        if self.GetHandler("on_setup"):
            runner.RunHandler(self, "on_setup", None)
        for m in self.childModels:
            m.RunSetup(runner)


class ViewProxy(object):
    """
    This class and its subclasses are the user-accessible objects exposed to event handler code.
    They purposefully contain no attributes for users to avoid, except a single _model reference.
    """

    scratchPoly = None      # Reuse this SAT.Polygon object for collision testing

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

    def send_message(self, message):
        if not isinstance(message, str):
            raise TypeError("send_message(): message must be a string")

        model = self._model
        if not model: return

        if model.stackManager.runner:
           model.stackManager.runner.RunHandler(model, "on_message", None, message)

    def focus(self):
        model = self._model
        if not model: return

        if model.stackManager.runner:
            model.stackManager.runner.SetFocus(self)

    @property
    def has_focus(self):
        model = self._model
        if not model: return False
        uiView = model.stackManager.GetUiViewByModel(model)
        if uiView and uiView.textbox:
            return context.stackWorker.focusedFabId == uiView.textbox
        return False

    def clone(self, name=None, **kwargs):
        model = self._model
        if not model: return None

        if model.type != "card":
            # update the model immediately on the runner thread
            newModel = model.CreateCopy(name)
            newModel.SetProperty("speed", model.GetProperty("speed"), notify=False)
            newModel.lastOnPeriodicTime = time()
            if not self.is_visible:
                newModel.SetProperty("is_visible", False, notify=False)
            for k,v in kwargs.items():
                if hasattr(newModel.GetProxy(), k):
                    setattr(newModel.GetProxy(), k, v)
                else:
                    raise TypeError(f"clone(): unable to set property {k}")

            model.stackManager.uiCard.model.AddChild(newModel)
            if not model.stackManager.isEditing:
                newModel.RunSetup(model.stackManager.runner)
                model.stackManager.runner.AddCardObj(newModel)

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
                    raise TypeError(f"clone(): unable to set property {k}")

        return newModel.GetProxy()

    def delete(self):
        model = self._model
        if not model or not model.parent or model.parent.type == "group":
            return

        if model.type != "card":
            model.stackManager.RemoveUiViewByModel(model)
        else:
            # When cloning a card, update the model and view together in a rare synchronous call to the main thread
            model.stackManager.RemoveCardRaw(model)

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

    def child_with_base_name(self, base):
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

    def flip_horizontal(self):
        model = self._model
        if not model: return
        model.PerformFlips(True, False)

    def flip_vertical(self):
        model = self._model
        if not model: return
        model.PerformFlips(False, True)

    def order_to_front(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(-1)

    def order_forward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(1)

    def order_backward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(-1)

    def order_to_back(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(0)

    def order_to_index(self, i):
        if not isinstance(i, int):
            raise TypeError("order_to_index(): index must be a number")

        model = self._model
        if not model: return

        if i < 0 or i >= len(model.parent.childModels):
            raise TypeError("order_to_index(): index is out of bounds")

        if model.didSetDown: return
        model.OrderMoveTo(i)

    def show(self):
        self.is_visible = True
    def hide(self):
        self.is_visible = False

    @property
    def is_visible(self):
        model = self._model
        if not model: return False
        return model.IsVisible()
    @is_visible.setter
    def is_visible(self, val):
        model = self._model
        if not model: return
        model.SetProperty("is_visible", bool(val))

    @property
    def rotation(self):
        model = self._model
        if not model: return 0
        return model.properties.get("rotation")
    @rotation.setter
    def rotation(self, val):
        if self._model.properties.get("rotation") is None:
            raise TypeError("object does not support rotation")
        if not isinstance(val, (int, float)):
            raise TypeError("rotation must be a number")
        model = self._model
        if not model: return
        model.SetProperty("rotation", val)

    def get_event_code(self, eventName):
        model = self._model
        if not model: return ""
        return model.handlers[eventName]

    def set_event_code(self, eventName, code):
        model = self._model
        if not model: return
        if not isinstance(eventName, str):
            raise TypeError("set_event_code(): eventName must be a string")
        if not isinstance(code, str):
            raise TypeError("set_event_code(): code must be a string")
        if eventName not in model.handlers:
            raise TypeError(f"set_event_code(): this object has no event called '{eventName}'")

        model.handlers[eventName] = code

    def set_bounce_objects(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError("set_bounce_objects(): objects needs to be a list of cardstock objects")
        models = [o._model for o in objects if isinstance(o, ViewProxy)]
        self._model.SetBounceModels(models)

    def stop_handling_mouse_event(self):
        self._model.stackManager.runner.stop_handling_mouse_event()

    def is_touching_point(self, point):
        if not isinstance(point, (wx.Point, wx.RealPoint, wx.CDSPoint, wx.CDSRealPoint, list, tuple)):
            raise TypeError("is_touching_point(): point needs to be a point or a list of two numbers")
        if len(point) != 2:
            raise TypeError("is_touching_point(): point needs to be a point or a list of two numbers")
        try:
            int(point[0]), int(point[1])
        except:
            raise ValueError("is_touching_point(): point needs to be a point or a list of two numbers")

        model = self._model
        if not model: return False
        if model.didSetDown: return False
        if model.type == "card":
            s = model.GetProperty('size')
            return point[0] >= 0 and point[1] >= 0 and point[0] <= s.width and point[1] <= s.height
        else:
            polys = model.GetPolygons()
            for poly in polys:
                if context.SAT.pointInPolygon(context.SAT.Vector.new(point.x, point.y), poly):
                    return True
            return False

    def is_touching(self, obj):
        if not isinstance(obj, ViewProxy):
            raise TypeError("is_touching(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel:
            return False

        polys = model.GetPolygons()
        oPolys = oModel.GetPolygons()
        for poly in polys:
            for oPoly in oPolys:
                if context.SAT.testPolygonPolygon(poly, oPoly):
                    return True
        return False

    def is_touching_edge(self, obj, skipIsTouchingCheck=False):
        if not isinstance(obj, ViewProxy):
            raise TypeError("is_touching_edge(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel: return []

        if model.didSetDown or oModel.didSetDown: return []

        if not skipIsTouchingCheck:
            if not self.is_touching(obj):
                return []

        rect = oModel.GetAbsoluteFrame() # other frame in card coords

        cornerSetback = 6
        # Pull edge lines away from the corners, so we don't always hit a corner when 2 objects touch
        rects = [wx.Rect(rect.TopLeft+(cornerSetback,0), rect.TopRight+(-cornerSetback,2)),
                 wx.Rect(rect.TopRight+(-2,cornerSetback), rect.BottomRight+(0,-cornerSetback)),
                 wx.Rect(rect.BottomLeft+(cornerSetback,-2), rect.BottomRight+(-cornerSetback,0)),
                 wx.Rect(rect.TopLeft+(0,cornerSetback), rect.BottomLeft+(2,-cornerSetback))]

        oRot = oModel.properties.get("rotation")
        if oRot is None: oRot = 0

        # if oRot == 0:
        bottom = rects[0]
        right = rects[1]
        top = rects[2]
        left = rects[3]

        if not ViewProxy.scratchPoly:
            ViewProxy.scratchPoly = context.SAT.Polygon.new(context.SAT.Vector.new(), [])

        def TestRect(r):
            points = (r.BottomLeft, r.BottomRight, r.TopRight, r.TopLeft)
            points = [context.SAT.Vector.new(p.x, p.y) for p in points]
            scratch = ViewProxy.scratchPoly
            scratch.setPoints(points)
            # scratch = context.SAT.Polygon.new(context.SAT.Vector.new(), points)
            polys = model.GetPolygons()
            for poly in polys:
                if context.SAT.testPolygonPolygon(poly, scratch):
                    return True
            return False

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
        return list(edges)

    def animate_position(self, duration, end_position, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_position(): duration must be a number")
        try:
            end_position = wx.RealPoint(end_position)
        except:
            raise ValueError("animate_position(): end_position must be a point or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origPosition = model.GetAbsolutePosition()
            offsetPt = end_position - tuple(origPosition)
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origPosition"] = origPosition
            animDict["offset"] = offset
            model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetAbsolutePosition(animDict["origPosition"] + tuple(animDict["offset"] * progress))

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def animate_center(self, duration, end_center, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_center(): duration must be a number")
        try:
            end_center = wx.RealPoint(end_center)
        except:
            raise ValueError("animate_center(): end_center must be a point or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origCenter = model.GetCenter()
            offsetPt = end_center - tuple(origCenter)
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origCenter"] = origCenter
            animDict["offset"] = offset
            self._model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetCenter(animDict["origCenter"] + tuple(animDict["offset"] * progress))

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def animate_size(self, duration, end_size, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_size(): duration must be a number")
        try:
            end_size = wx.Size(end_size)
        except:
            raise ValueError("animate_size(): end_size must be a size or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origSize = model.GetProperty("size")
            offset = wx.Size(end_size-tuple(origSize))
            animDict["origSize"] = origSize
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("size", animDict["origSize"] + tuple(animDict["offset"] * progress))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("size", duration, onUpdate, onStart, internalOnFinished)

    def animate_rotation(self, duration, end_rotation, force_direction=0, on_finished=None, *args, **kwargs):
        if self._model.properties.get("rotation") is None:
            raise TypeError("animate_rotation(): object does not support rotation")

        if not isinstance(duration, (int, float)):
            raise TypeError("animate_rotation(): duration must be a number")
        if not isinstance(end_rotation, (int, float)):
            raise TypeError("animate_rotation(): end_rotation must be a number")
        if not isinstance(force_direction, (int, float)):
            raise TypeError("animate_rotation(): force_direction must be a number")

        model = self._model
        if not model: return

        end_rotation = end_rotation

        def onStart(animDict):
            origVal = self.rotation
            animDict["origVal"] = origVal
            offset = end_rotation - origVal
            if force_direction:
                if force_direction > 0:
                    if offset <= 0: offset += 360
                elif force_direction < 0:
                    if offset >= 0: offset -= 360
            else:
                if offset > 180: offset -= 360
                if offset < -180: offset += 360
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("rotation", (animDict["origVal"] + animDict["offset"] * progress)%360)

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("rotation", duration, onUpdate, onStart, internalOnFinished)

    def stop_animating(self, property_name=None):
        model = self._model
        if not model: return
        model.StopAnimation(property_name)


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
        self.properties["can_save"] = False
        self.properties["can_resize"] = False

        self.propertyTypes["can_save"] = 'bool'
        self.propertyTypes["can_resize"] = 'bool'

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

        # Workaround for circular reference brython bug
        def touchData(d):
            if isinstance(d, dict):
                for v in d.values():
                    touchData(v)
            elif isinstance(d, (list, tuple)):
                for v in d:
                    touchData(v)
        touchData(data)

        return data

    def SetData(self, stackData):
        formatVer = stackData["CardStock_stack_format"]
        if formatVer != FILE_FORMAT_VERSION:
            migrations.MigrateDataFromFormatVersion(formatVer, stackData)

        super().SetData(stackData)
        self.childModels = []
        for data in stackData["cards"]:
            m = CardModel(self.stackManager)
            m.parent = self
            m.SetData(data)
            self.AppendCardModel(m)

        if formatVer != FILE_FORMAT_VERSION:
            migrations.MigrateModelFromFormatVersion(formatVer, self)


class Stack(ViewProxy):
    @property
    def num_cards(self):
        return len(self._model.childModels)

    @property
    def current_card(self):
        if self._model.didSetDown: return None
        return self._model.stackManager.uiCard.model.GetProxy()

    def card_with_number(self, number):
        model = self._model
        if model.didSetDown: return None
        if not isinstance(number, int):
            raise TypeError("card_with_number(): number is not an int")
        if number < 1 or number > len(model.childModels):
            raise ValueError("card_with_number(): number is out of bounds")
        return model.childModels[number-1].GetProxy()

    def return_from_stack(self, result=None):
        self._model.stackManager.runner.return_from_stack(result)

    def get_setup_value(self):
        return self._model.stackManager.runner.GetStackSetupValue()

    def add_card(self, name="card", atNumber=0):
        if not isinstance(name, str):
            raise TypeError("add_card(): name is not a string")
        atNumber = int(atNumber)
        if atNumber < 0 or atNumber > len(self._model.childModels)+1:
            raise ValueError("add_card(): atNumber is out of bounds")

        if self._model.didSetDown: return None
        return self._model.InsertNewCard(name, atNumber-1).GetProxy()


class CardModel(ViewModel):
    """
    The CardModel allows access to a few properties that actually live in the stack.  This is because the Designer
    allows editing cards, but not the stack model itself.  These properties are size, can_save, and can_resize.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "card"
        self.proxyClass = Card
        self.allChildModels = None

        # Add custom handlers to the top of the list
        handlers = {"on_setup": "", "on_show_card": "", "on_key_press": "", "on_key_hold": "", "on_key_release": ""}
        del self.handlers["on_bounce"]
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.handlers["on_resize"] = ""
        self.handlers["on_hide_card"] = ""
        self.handlers["on_exit_stack"] = ""
        self.initialEditHandler = "on_setup"

        # Custom property order and mask for the inspector
        self.properties["name"] = "card_1"
        self.properties["fill_color"] = "white"
        self.propertyKeys = ["name", "fill_color", "size", "can_save", "can_resize"]

        self.propertyTypes["fill_color"] = "color"
        self.propertyTypes["can_save"] = 'bool'
        self.propertyTypes["can_resize"] = 'bool'

    def SetProperty(self, key, value, notify=True):
        if key in ["size", "can_save", "can_resize"]:
            self.parent.SetProperty(key, value, notify)
            if key == "size":
                self.Notify("size")
        else:
            super().SetProperty(key, value, notify)

    def GetProperty(self, key):
        if key in ["size", "can_save", "can_resize"]:
            return self.parent.GetProperty(key)
        else:
            return super().GetProperty(key)

    def GetFrame(self):
        s = self.parent.GetProperty("size")
        return wx.Rect((0,0), s)

    def GetAbsoluteFrame(self):
        return self.GetFrame()

    def GetAllChildModels(self):
        if not self.allChildModels:
            self.allChildModels = []
            for child in self.childModels:
                self.allChildModels.append(child)
                if child.type == "group":
                    self.allChildModels.extend(child.GetAllChildModels())
        return self.allChildModels

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
        self.allChildModels = None
        self.InsertChild(model, len(self.childModels))

    def InsertChild(self, model, index):
        self.allChildModels = None
        self.childModels.insert(index, model)
        model.parent = self
        self.isDirty = True
        if self.stackManager.runner and self.stackManager.uiCard.model == self:
            model.stackManager.runner.AddCardObj(model)

    def RemoveChild(self, model):
        self.allChildModels = None
        self.childModels.remove(model)
        self.stackManager.delayedSetDowns.append(model)
        self.isDirty = True
        if self.stackManager.runner and self.stackManager.uiCard.model == self:
            model.stackManager.runner.RemoveCardObj(model)

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
                pos = m.properties["position"]
                size = m.properties["size"]
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

    def animate_fill_color(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_fill_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_fill_color(): end_color must be a string")

        model = self._model
        if not model: return

        end_color = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.fill_color)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("fill_color", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

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
            if not isinstance(p, (wx.Point, wx.RealPoint, wx.CDSPoint, wx.CDSRealPoint, list, tuple)):
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
            if not isinstance(p, (wx.Point, wx.RealPoint, wx.CDSPoint, wx.CDSRealPoint, list, tuple)):
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

        if model.didSetDown: return None
        g = model.stackManager.GroupModelsInternal(models, name=name)
        return g.GetProxy() if g else None

    def stop_all_animating(self, property_name=None):
        model = self._model
        if not model: return
        model.StopAnimation(property_name)
        for child in model.GetAllChildModels():
            child.StopAnimation(property_name)


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
        handlers = {"on_setup": "",
                    "on_click": "",
                    "on_selection_changed": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_click"

        self.properties["name"] = "button_1"
        self.properties["title"] = "Button"
        self.properties["style"] = "Border"
        self.properties["is_selected"] = False
        self.properties["rotation"] = 0.0

        self.propertyTypes["title"] = "string"
        self.propertyTypes["style"] = "choice"
        self.propertyTypes["is_selected"] = "bool"
        self.propertyTypes["rotation"] = "float"

        self.UpdatePropKeys("Border")

    def SetProperty(self, key, value, notify=True):
        if key == "style":
            self.UpdatePropKeys(value)
        elif key == "is_selected":
            if value != self.GetProperty("is_selected"):
                if value:
                    for m in self.get_radio_group():
                        if m.GetProperty("is_selected") and m != self:
                            m.SetProperty("is_selected", False)
                if self.stackManager:
                    if self.stackManager.runner and self.GetHandler("on_selection_changed"):
                        self.stackManager.runner.RunHandler(self, "on_selection_changed", None, value)
        super().SetProperty(key, value, notify)

    def SetData(self, data):
        super().SetData(data)
        self.UpdatePropKeys(self.properties["style"])

    def SetFromModel(self, model):
        super().SetFromModel(model)
        self.UpdatePropKeys(self.properties["style"])

    def UpdatePropKeys(self, style):
        # Custom property order and mask for the inspector
        if style in ("Border", "Borderless"):
            self.propertyKeys = ["name", "title", "style", "position", "size", "rotation"]
        else:
            self.propertyKeys = ["name", "title", "style", "is_selected", "position", "size", "rotation"]

    def get_radio_group(self):
        g = []
        if self.GetProperty("style") == "Radio" and self.parent:
            for m in self.parent.childModels:
                if m.type == "button" and m.GetProperty("style") == "Radio":
                    g.append(m)
        return g

    def get_radio_group_selection(self):
        g = self.get_radio_group()
        for m in g:
            if m.GetProperty("is_selected"):
                return m
        return None


class Button(ViewProxy):
    """
    Button proxy objects are the user-accessible objects exposed to event handler code for button objects.
    Based on ProxyView, and adds title, border, and click().
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
    def style(self):
        model = self._model
        if not model: return False
        return model.GetProperty("style")
    @style.setter
    def style(self, val):
        model = self._model
        if not model: return
        model.SetProperty("style", bool(val))

    @property
    def is_selected(self):
        model = self._model
        if not model: return False
        if model.GetProperty("style") in ("Border", "Borderless"):
            return False
        return model.GetProperty("is_selected")
    @is_selected.setter
    def is_selected(self, val):
        model = self._model
        if not model: return
        if model.GetProperty("style") not in ("Border", "Borderless"):
            model.SetProperty("is_selected", bool(val))

    def click(self):
        model = self._model
        if not model: return
        if model.stackManager.runner and model.GetHandler("on_click"):
            model.stackManager.runner.RunHandler(model, "on_click", None)

    def get_radio_group(self):
        model = self._model
        if not model: return []
        return [m.GetProxy() for m in model.get_radio_group()]

    def get_radio_group_selection(self):
        model = self._model
        if model:
            m = model.get_radio_group_selection()
            if m:
                return m.GetProxy()
        return None


class TextBaseModel(ViewModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.proxyClass = None

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["text_color"] = "black"
        self.properties["font"] = "Default"
        self.properties["font_size"] = 18
        self.properties["is_bold"] = False
        self.properties["is_italic"] = False
        self.properties["is_underlined"] = False

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["text_color"] = "color"
        self.propertyTypes["font"] = "choice"
        self.propertyTypes["font_size"] = "uint"
        self.propertyTypes["is_bold"] = "bool"
        self.propertyTypes["is_italic"] = "bool"
        self.propertyTypes["is_underlined"] = "bool"


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
    def text_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("text_color")
    @text_color.setter
    def text_color(self, val):
        if not isinstance(val, str):
            raise TypeError("text_color must be a string")
        model = self._model
        if not model: return
        model.SetProperty("text_color", val)

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
    def font_size(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("font_size")
    @font_size.setter
    def font_size(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("font_size must be a number")
        model = self._model
        if not model: return
        model.SetProperty("font_size", val)

    @property
    def is_bold(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("is_bold")
    @is_bold.setter
    def is_bold(self, val):
        if not isinstance(val, bool):
            raise TypeError("is_bold must be True or False")
        model = self._model
        if not model: return
        model.SetProperty("is_bold", val)

    @property
    def is_italic(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("is_italic")
    @is_italic.setter
    def is_italic(self, val):
        if not isinstance(val, bool):
            raise TypeError("is_italic must be True or False")
        model = self._model
        if not model: return
        model.SetProperty("is_italic", val)

    @property
    def is_underlined(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("is_underlined")
    @is_underlined.setter
    def is_underlined(self, val):
        if not isinstance(val, bool):
            raise TypeError("is_underlined must be True or False")
        model = self._model
        if not model: return
        if model.type == "textfield":
            raise TypeError("Text Field objects do not support underlined text.")
        model.SetProperty("is_underlined", val)

    def animate_font_size(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_font_size(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("animate_font_size(): end_thickness must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.font_size
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("font_size", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("font_size", duration, onUpdate, onStart, internalOnFinished)

    def animate_text_color(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_text_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_text_color(): end_color must be a string")

        model = self._model
        if not model: return

        end_color = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.text_color)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("text_color", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("text_color", duration, onUpdate, onStart, internalOnFinished)


class TextLabelModel(TextBaseModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textlabel"
        self.proxyClass = TextLabel
        self.properties["name"] = "label_1"
        self.properties["can_auto_shrink"] = True
        self.properties["rotation"] = 0.0

        self.propertyTypes["can_auto_shrink"] = "bool"
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "font_size", "text_color", "can_auto_shrink", "position", "size", "rotation"]


class TextLabel(TextBaseProxy):
    """
    TextLabel proxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    @property
    def can_auto_shrink(self):
        model = self._model
        if not model: return False
        return model.GetProperty("can_auto_shrink")
    @can_auto_shrink.setter
    def can_auto_shrink(self, val):
        model = self._model
        if not model: return
        model.SetProperty("can_auto_shrink", bool(val))


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
        handlers = {"on_setup": "", "on_text_changed": "", "on_text_enter": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_text_enter"

        self.properties["name"] = "field_1"
        self.properties["is_editable"] = True
        self.properties["is_multiline"] = False
        self.properties["font_size"] = 12

        self.propertyTypes["is_editable"] = "bool"
        self.propertyTypes["is_multiline"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "font_size", "text_color", "is_editable", "is_multiline", "position", "size"]

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
    def is_editable(self):
        model = self._model
        if not model: return False
        return model.GetProperty("is_editable")
    @is_editable.setter
    def is_editable(self, val):
        model = self._model
        if not model: return
        model.SetProperty("is_editable", bool(val))

    @property
    def is_multiline(self):
        model = self._model
        if not model: return False
        return model.GetProperty("is_multiline")
    @is_multiline.setter
    def is_multiline(self, val):
        model = self._model
        if not model: return
        model.SetProperty("is_multiline", bool(val))

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
    def selected_text(self):
        model = self._model
        if not model: return False
        return model.GetSelectedText()
    @selected_text.setter
    def selected_text(self, val):
        model = self._model
        if not model: return
        if isinstance(val,str):
            model.SetSelectedText(val)
            return
        raise TypeError("selected_text must be a string")

    def select_all(self):
        model = self._model
        if not model: return
        model.Notify("selectAll")

    def enter(self):
        model = self._model
        if not model: return
        if model.didSetDown: return
        model.stackManager.runner.RunHandler(model, "on_text_enter", None)


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
            model.origGroupSubviewRotation = model.properties.get("rotation")

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            model = self.stackManager.ModelFromData(self.stackManager, childData)
            model.parent = self
            self.childModels.append(model)
            model.origGroupSubviewFrame = model.GetFrame()
            model.origGroupSubviewRotation = model.properties.get("rotation")
        self.origFrame = self.GetFrame()

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        super().SetProperty(key, value, notify)
        if key == "is_visible":
            for m in self.GetAllChildModels():
                m.Notify("is_visible")

    def AddChildModels(self, models):
        selfPos = self.properties["position"]
        for model in models:
            self.childModels.append(model)
            model.parent = self
            pos = model.properties["position"]
            model.SetProperty("position", [pos[0]-selfPos[0], pos[1]-selfPos[1]], notify=False)
        self.UpdateFrame()
        self.origFrame = self.GetFrame()
        for model in models:
            model.origGroupSubviewFrame = model.GetFrame()
            model.origGroupSubviewRotation = model.properties.get("rotation")
        self.Notify("child")
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        del model.origGroupSubviewFrame
        del model.origGroupSubviewRotation
        pos = model.properties["position"]
        selfPos = self.properties["position"]
        model.SetProperty("position", [pos[0]+selfPos[0], pos[1]+selfPos[1]], notify=False)
        self.stackManager.delayedSetDowns.append(model)
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
                oldPos = m.properties["position"]
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
                    rot = m.properties.get("rotation")
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
                size = wx.Size(abs(size[0]), abs(size[1]))
                m.SetFrame(wx.Rect(center - tuple(size/2), size))


class Group(ViewProxy):
    """
    Group proxy objects are the user-accessible objects exposed to event handler code for group objects.
    """

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
        handlers = {"on_setup": "", "on_done_loading": "", "on_card_stock_link": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_done_loading"

        self.properties["name"] = "webview_1"
        self.properties["URL"] = ""
        self.properties["HTML"] = ""
        self.properties["allowed_hosts"] = []
        self.propertyTypes["URL"] = "string"
        self.propertyTypes["HTML"] = "string"
        self.propertyTypes["allowed_hosts"] = "list"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "URL", "allowed_hosts", "position", "size"]

    def SetProperty(self, key, value, notify=True):
        if key == "URL":
            if len(value):
                parts = urlparse(value)
                if not parts.scheme:
                    value = "https://" + value
        elif key == "allowed_hosts":
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
    def allowed_hosts(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("allowed_hosts")
    @allowed_hosts.setter
    def allowed_hosts(self, val):
        if not isinstance(val, (list, tuple)):
            raise TypeError("allowed_hosts must be set to a list value")
        model = self._model
        if not model: return
        model.SetProperty("allowed_hosts", val)

    @property
    def can_go_back(self):
        return False

    @property
    def can_go_forward(self):
        return False

    def go_back(self):
        pass

    def go_forward(self):
        pass

    def run_java_script(self, code):
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
        self.isPolyRect = False

        if shapeType == "pen":
            self.properties["name"] = "line_1"
        elif shapeType == "polygon":
            self.properties["name"] = "polygon_1"
        else:
            self.properties["name"] = f"{shapeType}_1"

        self.properties["originalSize"] = None
        self.properties["pen_color"] = "black"
        self.properties["pen_thickness"] = 2
        self.properties["rotation"] = 0.0

        self.propertyTypes["originalSize"] = "size"
        self.propertyTypes["pen_color"] = "color"
        self.propertyTypes["pen_thickness"] = "uint"
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "pen_color", "pen_thickness", "position", "size", "rotation"]

    def GetData(self):
        data = super().GetData()
        data["points"] = [[p[0], p[1]] for p in self.points]
        return data

    def SetData(self, data):
        super().SetData(data)
        self.type = data["type"]
        self.points = [[int(float(p[0])), int(float(p[1]))] for p in data["points"]]

    def SetShape(self, shape):
        self.type = shape["type"]
        self.properties["pen_color"] = shape["pen_color"]
        self.properties["pen_thickness"] = shape["thickness"]
        self.points = shape["points"]
        self.isDirty = True
        self.Notify("shape")

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        if key == "size":
            self.scaledPoints = None
        super().SetProperty(key, value, notify)

    def MakePolygon(self):
        if self.type in ["line", "pen"]:
            points = self.GetAbsolutePoints()
            self.polygons = []
            if len(points) > 1:
                oldP = points[0]
                for p in points[1:]:
                    self.polygons.append(context.SAT.Polygon.new(context.SAT.Vector.new(),
                                                                [context.SAT.Vector.new(oldP[0], oldP[1]),
                                                                 context.SAT.Vector.new(p[0], p[1])]))
                    oldP = p
        else:
            super().MakePolygon()

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
        size = self.properties["size"]

        if not origSize or origSize[0] == 0 or origSize[1] == 0:
            return self.points
        scaleX = 1
        scaleY = 1
        if origSize[0] != 0:
            scaleX = size[0] / origSize[0]
        if origSize[1] != 0:
            scaleY = size[1] / origSize[1]
        points = [wx.Point(p[0] * scaleX, p[1] * scaleY) for p in self.points]
        self.scaledPoints = points
        return self.scaledPoints

    def GetAbsolutePoints(self):
        pos = self.GetAbsolutePosition()
        return [pos + p for p in self.GetScaledPoints()]

    @staticmethod
    def RectFromPoints(points):
        rect = wx.Rect(points[0][0], points[0][1], 0, 0)
        for x, y in points[1:]:
            if x < rect.Left:
                rect.Width += rect.Left - x
                rect.Left = x
            elif x > rect.Left + rect.Width:
                rect.Width = x - rect.Left
            if y < rect.Top:
                rect.Height += rect.Top - y
                rect.Top = y
            elif y > rect.Top + rect.Height:
                rect.Height = y - rect.Top
        return rect

    # Re-fit the bounding box to the shape
    def ReCropShape(self):
        if len(self.points) == 0:
            return

        oldSize = self.properties["size"] if self.properties["originalSize"] else None

        # First move all points to be relative to the card origin
        offset = self.properties["position"]
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
        self.SetProperty("position", rect.Position, notify=False)
        if rect.Width < self.minSize.width: rect.Width = self.minSize.width
        if rect.Height < self.minSize.height: rect.Height = self.minSize.height

        if oldSize:
            self.SetProperty("size", [oldSize[0], oldSize[1]], notify=False)
        else:
            self.SetProperty("size", rect.Size, notify=False)
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
    def pen_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("pen_color")
    @pen_color.setter
    def pen_color(self, val):
        if not isinstance(val, str):
            raise TypeError("pen_color must be a string")
        model = self._model
        if not model: return
        model.SetProperty("pen_color", val)

    @property
    def pen_thickness(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("pen_thickness")
    @pen_thickness.setter
    def pen_thickness(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("pen_thickness must be a number")
        model = self._model
        if not model: return
        model.SetProperty("pen_thickness", val)

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

    def animate_pen_thickness(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_pen_thickness(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("animate_pen_thickness(): end_thickness must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.pen_thickness
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("pen_thickness", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("pen_thickness", duration, onUpdate, onStart, internalOnFinished)

    def animate_pen_color(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_pen_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_pen_color(): end_color must be a string")

        model = self._model
        if not model: return

        end_color = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.pen_color)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("pen_color", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("pen_color", duration, onUpdate, onStart, internalOnFinished)


class ShapeModel(LineModel):
    """
    This is the model class for Oval and Rectangle objects, and the superclass for models for round-rects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = Shape

        self.properties["fill_color"] = "white"
        self.propertyTypes["fill_color"] = "color"
        if shapeType in ["oval", "polygon"]:
            self.isPolyRect = False

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "pen_color", "pen_thickness", "fill_color", "position", "size", "rotation"]

    def MakePolygon(self):
        if self.type == "polygon":
            t = self.properties['pen_thickness'] / 2
            points = self.GetAbsolutePoints()
            points = [(p.x+t, p.y-t) for p in points]
            if context.decomp.makeCCW(points):
                points.reverse()
            convexPolygons = context.decomp.quickDecomp(points)
            self.polygons = []
            for poly in convexPolygons:
                self.polygons.append(context.SAT.Polygon.new(context.SAT.Vector.new(),
                                                            [context.SAT.Vector.new(p[0], p[1]) for p in poly]))
        elif self.type == "oval":
            t = self.properties['pen_thickness'] / 2
            rX = self.properties['size'].width/2 + t
            rY = self.properties['size'].height/2 + t
            if min(rX, rY) < 12:
                # Tiny oval? just use a rect.
                super().MakePolygon()
            else:
                n = 20  # points to generate
                ellipsePoints = [
                    (rX * math.cos(theta) + rX-t, rY * math.sin(theta) + rY-t)
                    for theta in (math.pi * 2 * i / n for i in range(n))
                ]
                ellipsePoints = self.RotatedPoints(ellipsePoints)
                self.polygons = [context.SAT.Polygon.new(context.SAT.Vector.new(),
                                                        [context.SAT.Vector.new(p.x, p.y) for p in ellipsePoints])]
        elif self.type == "rect":
            super().MakePolygon()

    def SetShape(self, shape):
        self.properties["fill_color"] = shape["fill_color"]
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

    def animate_fill_color(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_fill_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_fill_color(): end_color must be a string")

        model = self._model
        if not model: return

        end_color = wx.Colour(endVal)

        def onStart(animDict):
            origVal = wx.Colour(self.fill_color)
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            animDict["origParts"] = origParts
            endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
            animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

        def onUpdate(progress, animDict):
            model.SetProperty("fill_color", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("fill_color", duration, onUpdate, onStart, internalOnFinished)


class RoundRectModel(ShapeModel):
    """
    This is the model class for Round Rectangle objects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = RoundRect

        self.properties["corner_radius"] = 8
        self.propertyTypes["corner_radius"] = "uint"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "pen_color", "pen_thickness", "fill_color", "corner_radius", "position", "size", "rotation"]

    def MakePolygon(self):
        t = self.properties['pen_thickness'] / 2
        s = self.GetProperty('size')
        f = wx.Rect(-t, -t, s[0]+2*t, s[1]+2*t)
        points = [f.BottomLeft, f.BottomRight, f.TopRight, f.TopLeft]
        points = self.RotatedPoints(points)
        self.polygons = [context.SAT.Polygon.new(context.SAT.Vector.new(),
                                              [context.SAT.Vector.new(p.x, p.y) for p in points])]

    def SetShape(self, shape):
        self.properties["corner_radius"] = shape["corner_radius"] if "corner_radius" in shape else 8
        super().SetShape(shape)


class RoundRect(Shape):
    """
    RoundRect proxy objects are the user-accessible objects exposed to event handler code for round rect objects.
    They're extended from ShapeProxy, which is extended from the Line proxy class.
    """

    @property
    def corner_radius(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("corner_radius")
    @corner_radius.setter
    def corner_radius(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("corner_radius must be a number")
        model = self._model
        if not model: return
        model.SetProperty("corner_radius", val)

    def animate_corner_radius(self, duration, endVal, on_finished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_corner_radius(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("animate_corner_radius(): end_corner_radius must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.corner_radius
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("corner_radius", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished, *args, **kwargs)

        model.AddAnimation("corner_radius", duration, onUpdate, onStart, internalOnFinished)
