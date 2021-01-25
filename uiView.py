#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
import ast
import re

class UiView(object):
    def __init__(self, parent, stackView, model, view):
        super().__init__()
        self.stackView = stackView
        self.parent = parent
        self.view = view
        self.model = None
        self.SetModel(model)

        self.isSelected = False

        self.SetView(view)

        self.lastEditedHandler = None
        self.delta = ((0, 0))

    def BindEvents(self, view):
        view.Bind(wx.EVT_ENTER_WINDOW, self.FwdOnMouseEnter)
        view.Bind(wx.EVT_LEAVE_WINDOW, self.FwdOnMouseExit)
        view.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        view.Bind(wx.EVT_MOTION, self.FwdOnMouseMove)
        view.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseUp)
        view.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        view.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

        view.Bind(wx.EVT_SIZE, self.OnResize)

    def FwdOnMouseDown( self, event): self.stackView.OnMouseDown( self, event)
    def FwdOnMouseMove( self, event): self.stackView.OnMouseMove( self, event)
    def FwdOnMouseUp(   self, event): self.stackView.OnMouseUp(   self, event)
    def FwdOnMouseEnter(self, event): self.stackView.OnMouseEnter(self, event)
    def FwdOnMouseExit( self, event): self.stackView.OnMouseExit( self, event)
    def FwdOnKeyDown(   self, event): self.stackView.OnKeyDown(   self, event)
    def FwdOnKeyUp(     self, event): self.stackView.OnKeyUp(     self, event)

    def SetView(self, view):
        self.view = view
        self.BindEvents(view)

        if self.GetCursor():
            self.view.SetCursor(wx.Cursor(self.GetCursor()))

        viewSize = list(self.view.GetSize())
        self.selectionBox = wx.Window(parent=self.view, id=wx.ID_ANY, pos=(0,0), size=viewSize, style=0)
        self.selectionBox.Bind(wx.EVT_PAINT, self.OnPaintSelectionBox)
        self.selectionBox.SetBackgroundColour(None)
        self.selectionBox.Enable(False)
        self.selectionBox.Hide()

        self.resizeBox = wx.Window(parent=self.view, id=wx.ID_ANY, pos=(viewSize[0]-10, viewSize[1]-10), size=(10,10), style=0)
        self.resizeBox.SetBackgroundColour('Blue')
        self.resizeBox.Enable(False)
        self.resizeBox.Hide()

        mSize = self.model.GetProperty("size")
        if mSize[0] > 0 and mSize[1] > 0:
            self.view.SetSize(mSize)
            self.view.SetPosition(self.model.GetProperty("position"))

        self.view.Show(not self.model.GetProperty("hidden"))

    def SetModel(self, model):
        if self.model:
            self.model.RemovePropertyListener(self.OnPropertyChanged)
        self.model = model
        self.lastEditedHandler = None
        self.model.AddPropertyListener(self.OnPropertyChanged)

    def GetCursor(self):
        return wx.CURSOR_HAND

    def OnPropertyChanged(self, model, key):
        if key == "size":
            s = list(self.model.GetProperty(key))
            self.view.SetSize(s)
        elif key == "position":
            self.view.SetPosition(self.model.GetProperty(key))
        elif key == "hidden":
            self.view.Show(not self.model.GetProperty(key))

    def OnResize(self, event):
        w, h = self.view.GetSize()
        self.selectionBox.SetSize(w, h)
        x,y = self.view.GetPosition()
        if self.resizeBox:
            self.resizeBox.SetRect((w-10, h-10, 10, 10))
        event.Skip()

    def DestroyView(self):
        self.model.RemovePropertyListener(self.OnPropertyChanged)
        self.selectionBox.Destroy()
        if self.resizeBox:
            self.resizeBox.Destroy()
        self.view.Destroy()
        self.view = None

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        self.isSelected = selected
        self.selectionBox.Show(selected)
        if self.resizeBox:
            self.resizeBox.Show(selected)
        self.view.Refresh()
        self.view.Update()

    def OnMouseDown(self, event):
        if self.model.runner and "OnMouseDown" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnMouseDown", event)
        event.Skip()

    def OnMouseMove(self, event):
        if self.model.runner and "OnMouseMove" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnMouseMove", event)
        event.Skip()

    def OnMouseUp(self, event):
        if self.model.runner and "OnMouseUp" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnMouseUp", event)
        event.Skip()

    def OnMouseEnter(self, event):
        if self.model.runner and "OnMouseEnter" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnMouseEnter", event)
        event.Skip()

    def OnMouseExit(self, event):
        if self.model.runner and "OnMouseExit" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnMouseExit", event)
        event.Skip()

    def OnIdle(self, event):
        if self.model.runner and "OnIdle" in self.model.handlers:
            self.model.runner.RunHandler(self.model, "OnIdle", event)


    def OnPaintSelectionBox(self, event):
        dc = wx.PaintDC(self.selectionBox)
        dc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
        dc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle((1, 1), (self.selectionBox.GetSize()[0]-1, self.selectionBox.GetSize()[1]-1))

    handlerDisplayNames = {
        'OnClick':      "OnClick():",
        'OnTextEnter':  "OnTextEnter():",
        'OnTextChanged':"OnTextChanged():",
        'OnMouseDown':  "OnMouseDown(mouseX, mouseY):",
        'OnMouseMove':  "OnMouseMove(mouseX, mouseY):",
        'OnMouseUp':    "OnMouseUp(mouseX, mouseY):",
        'OnMouseEnter': "OnMouseEnter(mouseX, mouseY):",
        'OnMouseExit':  "OnMouseExit(mouseX, mouseY):",
        'OnMessage':    "OnMessage(message):",
        'OnStackStart': "OnStackStart():",
        'OnShowCard':   "OnShowCard():",
        'OnHideCard':   "OnHideCard():",
        'OnIdle':       "OnIdle():",
        'OnKeyDown':    "OnKeyDown(keyName):",
        'OnKeyUp':      "OnKeyUp(keyName):"
    }


class ViewModel(object):
    minSize = (20,20)

    def __init__(self):
        super().__init__()
        self.type = None
        self.parent = None
        self.handlers = {"OnMouseDown": "",
                         "OnMouseMove": "",
                         "OnMouseUp": "",
                         "OnMouseEnter": "",
                         "OnMouseExit": "",
                         "OnMessage": "",
                         "OnIdle": ""
                         }
        self.properties = {"name": "",
                           "size": (0,0),
                           "position": (0,0),
                           "hidden": False,
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "point",
                              "size": "point",
                              "hidden": "bool"}
        self.propertyChoices = {}

        self.propertyListeners = []

        self.runner = None
        self.isDirty = False

    def GetType(self):
        return self.type

    def SetDirty(self, isDirty):
        self.isDirty = isDirty

    def GetDirty(self):
        return self.isDirty

    def GetAbsolutePosition(self):
        pos = self.GetProperty("position").copy()  # Copy so we don't edit the model's position
        parent = self.parent
        while parent and parent.type != "card":
            parentPos = parent.GetProperty("position")
            pos[0] += parentPos[0]
            pos[1] += parentPos[1]
            parent = parent.parent
        return pos

    def SetAbsolutePosition(self, pos):
        parent = self.parent
        while parent and parent.type != "card":
            parentPos = parent.GetProperty("position")
            pos[0] -= parentPos[0]
            pos[1] -= parentPos[1]
            parent = parent.parent
        self.SetProperty("position", pos)

    def GetFrame(self):
        p = wx.Point(self.GetProperty("position"))
        s = wx.Size(self.GetProperty("size"))
        return wx.Rect(p, s)

    def GetAbsoluteFrame(self):
        p = wx.Point(self.GetAbsolutePosition())
        s = wx.Size(self.GetProperty("size"))
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

        return {"type": self.type,
                "handlers": handlers,
                "properties": props}

    def SetData(self, data):
        for k, v in data["handlers"].items():
            self.handlers[k] = v
        for k, v in data["properties"].items():
            self.SetProperty(k, v)

    def SetFromModel(self, model):
        for k, v in model.handlers.items():
            self.handlers[k] = v
        for k, v in model.properties.items():
            self.SetProperty(k, v)

    # Custom property order and mask for the inspector
    def PropertyKeys(self):
        return self.propertyKeys

    # Options currently are string, bool, int, float, point, choice
    def GetPropertyType(self, key):
        return self.propertyTypes[key]

    def GetPropertyChoices(self, key):
        return self.propertyChoices[key]

    def AddPropertyListener(self, callback):
        self.propertyListeners.append(callback)

    def RemovePropertyListener(self, callback):
        self.propertyListeners.remove(callback)

    def RemoveAllPropertyListeners(self):
        self.propertyListeners = []

    def GetProperty(self, key):
        if key in self.properties:
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

    def Notify(self, key):
        for callback in self.propertyListeners:
            callback(self, key)

    def SetProperty(self, key, value, notify=True):
        if key in self.propertyTypes and self.propertyTypes[key] == "point":
            value = list(value)

        if key == "name":
            value = re.sub(r'\W+', '', value)
            if not re.match(r'[A-Za-z_][A-Za-z_0-9]*', value):
                if notify:
                    self.Notify(key)
                return
        elif key == "size":
            if value[0] < self.minSize[0]: value[0] = self.minSize[0]
            if value[1] < self.minSize[1]: value[1] = self.minSize[1]

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
            elif propType == "point":
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

    def DeduplicateName(self, name, existingNames):
        existingNames.extend(["card", "self", "keyName", "mouseX",  "mouseY", "message"]) # disallow globals
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

    def SendMessage(self, message):
        if self.runner:
            self.runner.RunHandler(self, "OnMessage", None, message)

    def Focus(self):
        if self.runner:
            self.runner.SetFocus(self)

    def Show(self): self.SetProperty("hidden", False)
    def Hide(self): self.SetProperty("hidden", True)
    def SetVisible(self, visible): self.SetProperty("hidden", not visible)
    def GetVisible(self): return not self.GetProperty("hidden")

    def GetSize(self): return list(self.GetProperty("size"))
    def SetSize(self, size): self.SetProperty("size", size)

    def GetPosition(self): return self.GetAbsolutePosition()
    def SetPosition(self, pos): self.SetAbsolutePosition(pos)
    def GetCenter(self):
        p = self.GetAbsolutePosition()
        s = self.GetProperty("size")
        return [p[0]+s[0]/2, p[1]+s[1]/2]
    def SetCenter(self, center):
        s = self.GetProperty("size")
        self.SetAbsolutePosition([center[0]-s[0]/2, center[1]-s[1]/2])
    def MoveBy(self, delta):
        pos = self.GetProperty("position")
        self.SetProperty("position", (pos[0]+delta[0], pos[1]+delta[1]))

    def IsTouching(self, model):
        sf = self.GetAbsoluteFrame() # self frame in card coords
        f = model.GetAbsoluteFrame() # other frame in card soords
        return sf.Intersects(f)

    def IsTouchingEdge(self, model):
        sf = self.GetAbsoluteFrame() # self frame in card coords
        f = model.GetAbsoluteFrame() # other frame in card soords
        top = wx.Rect(f.Left, f.Top, f.Width, 1)
        bottom = wx.Rect(f.Left, f.Bottom, f.Width, 1)
        left = wx.Rect(f.Left, f.Top, 1, f.Height)
        right = wx.Rect(f.Right, f.Top, 1, f.Height)
        if sf.Intersects(top): return "Top"
        if sf.Intersects(bottom): return "Bottom"
        if sf.Intersects(left): return "Left"
        if sf.Intersects(right): return "Right"
        return False
