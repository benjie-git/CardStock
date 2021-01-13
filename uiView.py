#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from wx.lib.docview import Command
import ast


class UiView(object):
    def __init__(self, stackView, model, view):
        super().__init__()
        self.stackView = stackView
        self.SetModel(model)

        self.isSelected = False

        self.SetView(view)

        self.lastEditedHandler = None
        self.delta = ((0, 0))
        self.minSize = (20,20)

    def BindEvents(self, view):
        view.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        view.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
        view.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        view.Bind(wx.EVT_MOTION, self.OnMouseMove)
        view.Bind(wx.EVT_SIZE, self.OnResize)
        view.Bind(wx.EVT_KEY_DOWN, self.OnArrowKeyDown)
        if self.model.type != "card":
            view.Bind(wx.EVT_MOTION, self.stackView.uiCard.OnMouseMove)
        view.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)

    def SetView(self, view):
        self.view = view
        self.BindEvents(view)

        viewSize = list(self.view.GetSize())
        self.selectionBox = wx.Window(parent=self.view, id=wx.ID_ANY, pos=(0,0), size=viewSize, style=0)
        self.selectionBox.Bind(wx.EVT_PAINT, self.OnPaintSelectionBox)
        self.selectionBox.SetBackgroundColour(None)
        self.selectionBox.Enable(False)
        self.selectionBox.Hide()

        if self.model.type != "card":
            self.resizeBox = wx.Window(parent=self.view, id=wx.ID_ANY, pos=(viewSize[0]-10, viewSize[1]-10), size=(10,10), style=0)
            self.resizeBox.SetBackgroundColour('Blue')
            self.resizeBox.Enable(False)
            self.resizeBox.Hide()
        else:
            self.resizeBox = None

        mSize = self.model.GetProperty("size")
        if mSize[0] > 0 and mSize[1] > 0:
            self.view.SetSize(mSize)
            self.view.SetPosition(self.model.GetProperty("position"))

        self.view.Show(not self.model.GetProperty("hidden"))


    def SetModel(self, model):
        self.model = model
        self.model.AddPropertyListener(self.OnPropertyChanged)

    def OnPropertyChanged(self, model, key):
        if key == "size":
            self.view.SetSize(self.model.GetProperty(key))
        elif key == "position":
            self.view.SetPosition(self.model.GetProperty(key))
        elif key == "hidden":
            self.view.Show(not self.model.GetProperty(key))

    def OnResize(self, event):
        setW, setH = self.view.GetSize()
        w, h = (setW, setH)
        if w < 20:
            w = 20
        if h < 20:
            h = 20
        if w != setW or h != setH:
            self.view.SetSize(w, h)
            self.model.SetProperty("size", [w,h])
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
        if self.stackView.isEditing:
            if self.model.type != "card" and not self.stackView.isInDrawingMode:
                self.view.CaptureMouse()
                x, y = self.stackView.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
                originx, originy = self.view.GetPosition()
                dx = x - originx
                dy = y - originy
                self.moveOrigin = (originx, originy)
                self.origMousePos = (x, y)
                self.origSize = list(self.view.GetSize())
                self.delta = ((dx, dy))

                rpx,rpy = event.GetPosition()
                hackOffset = 5 if self.model.type == "button" else 0  # Buttons are bigger than specified???
                if self.origSize[0] - rpx + hackOffset < 10 and self.origSize[1] - rpy + hackOffset < 10:
                    self.isResizing = True
                else:
                    self.isResizing = False
            if not self.stackView.isInDrawingMode:
                self.stackView.SelectUiView(self)
            else:
                event.Skip()
        else:
            if self.model.runner and "OnMouseDown" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnMouseDown", event)
            event.Skip()

    def OnMouseMove(self, event):
        if self.model.type != "card" and self.stackView.isEditing and not self.stackView.isInDrawingMode and event.Dragging():
            x, y = self.stackView.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
            if not self.isResizing:
                fp = (x - self.delta[0], y - self.delta[1])
                self.view.Move(fp)
            else:
                offset = (x-self.origMousePos[0], y-self.origMousePos[1])
                self.view.SetSize(self.origSize[0]+offset[0], self.origSize[1]+offset[1])
        elif not self.stackView.isEditing:
            if self.model.runner and "OnMouseMove" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnMouseMove", event)
        event.Skip()

    def OnMouseUp(self, event):
        if self.model.type != "card" and self.stackView.isEditing and not self.stackView.isInDrawingMode and self.view.HasCapture():
            self.view.ReleaseMouse()
            if not self.isResizing:
                endx, endy = self.view.GetPosition()
                offset = (endx-self.moveOrigin[0], endy-self.moveOrigin[1])
                if offset != (0, 0):
                    command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, self.model, offset)
                    self.view.SetPosition(self.moveOrigin)
                    self.stackView.command_processor.Submit(command)
            else:
                endw, endh = self.view.GetSize()
                offset = (endw-self.origSize[0], endh-self.origSize[1])
                if offset != (0, 0):
                    command = ResizeUiViewCommand(True, 'Resize', self.stackView, self.stackView.cardIndex, self.model, offset)
                    self.view.SetSize(self.origSize)
                    self.stackView.command_processor.Submit(command)

            self.stackView.SetFocus()
        elif not self.stackView.isEditing:
            if self.model.runner and "OnMouseUp" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnMouseUp", event)
        event.Skip()

    def OnArrowKeyDown(self, event):
        if self.stackView.isEditing:
            uiView = self
            if self.model.type == "card":
                uiView = self.stackView.GetSelectedUiView()

            if not uiView: return

            code = event.GetKeyCode()
            if uiView.model.type != "card":
                pos = wx.Point(uiView.model.GetProperty("position"))
                cardRect = self.stackView.GetRect()
                dist = 20 if event.AltDown() else (5 if event.ShiftDown() else 1)
                if code == wx.WXK_LEFT:
                    if pos.x-dist < 0: dist = pos.x
                    if dist > 0:
                        command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (-dist, 0))
                        self.stackView.command_processor.Submit(command)
                        uiView.model.SetProperty("position", (pos.x-dist, pos.y))
                elif code == wx.WXK_RIGHT:
                    if pos.x+dist > cardRect.Right-20: dist = cardRect.Right-20 - pos.x
                    if dist > 0:
                        command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (dist, 0))
                        self.stackView.command_processor.Submit(command)
                        uiView.model.SetProperty("position", (pos.x+dist, pos.y))
                elif code == wx.WXK_UP:
                    if pos.y-dist < 0: dist = pos.y
                    if dist > 0:
                        command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (0, -dist))
                        self.stackView.command_processor.Submit(command)
                        uiView.model.SetProperty("position", (pos.x, pos.y-dist))
                elif code == wx.WXK_DOWN:
                    if pos.y+dist > cardRect.Bottom-20: dist = cardRect.Bottom-20 - pos.y
                    if dist > 0:
                        command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (0, dist))
                        self.stackView.command_processor.Submit(command)
                        uiView.model.SetProperty("position", (pos.x, pos.y+dist))

            if code == wx.WXK_TAB:
                    ui = self.stackView.GetSelectedUiView()
                    if ui == self.stackView.uiCard:
                        self.stackView.SelectUiView(self.stackView.uiViews[0])
                    elif ui == self.stackView.uiViews[-1]:
                        self.stackView.SelectUiView(self.stackView.uiCard)
                    else:
                        nextUi = self.stackView.uiViews[self.stackView.uiViews.index(ui) + 1]
                        self.stackView.SelectUiView(nextUi)
        else:
            event.Skip()

    def OnMouseEnter(self, event):
        if not self.stackView.isEditing:
            if self.model.runner and "OnMouseEnter" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnMouseEnter", event)
            event.Skip()

    def OnMouseExit(self, event):
        if not self.stackView.isEditing:
            if self.model.runner and "OnMouseExit" in self.model.handlers:
                self.model.runner.RunHandler(self.model, "OnMouseExit", event)
            event.Skip()

    def OnPaintSelectionBox(self, event):
        dc = wx.PaintDC(self.selectionBox)
        dc.SetPen(wx.Pen('Blue', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle((1, 1), (self.selectionBox.GetSize()[0]-1, self.selectionBox.GetSize()[1]-1))

    handlerDisplayNames = {
        'OnClick':      "def OnClick():",
        'OnTextEnter':  "def OnTextEnter():",
        'OnTextChanged':"def OnTextChanged():",
        'OnMouseDown':  "def OnMouseDown(mouseX, mouseY):",
        'OnMouseMove':  "def OnMouseMove(mouseX, mouseY):",
        'OnMouseUp':    "def OnMouseUp(mouseX, mouseY):",
        'OnMouseEnter': "def OnMouseEnter(mouseX, mouseY):",
        'OnMouseExit':  "def OnMouseExit(mouseX, mouseY):",
        'OnMessage':    "def OnMessage(message):",
        'OnStart':      "def OnStart():",
        'OnShowCard':   "def OnShowCard():",
        'OnHideCard':   "def OnHideCard():",
        'OnIdle':       "def OnIdle():",
        'OnKeyDown':    "def OnKeyDown(key):",
        'OnKeyUp':      "def OnKeyUp(key):",
    }


class ViewModel(object):
    def __init__(self):
        super().__init__()
        self.type = None
        self.handlers = {"OnMouseDown": "",
                         "OnMouseMove": "",
                         "OnMouseUp": "",
                         "OnMouseEnter": "",
                         "OnMouseExit": "",
                         "OnMessage": "",
                         "OnStart": "",
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

    def GetFrame(self):
        p = wx.Point(self.properties["position"])
        s = wx.Size(self.properties["size"])
        return wx.Rect(p, s)

    def GetData(self):
        handlers = {}
        for k, v in self.handlers.items():
            if len(v.strip()) > 0:
                handlers[k] = v

        return {"type": self.type,
                "handlers": handlers,
                "properties": self.properties}

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
        # if callback in self.propertyListeners:
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

    def SetProperty(self, key, value):
        if isinstance(value, wx.Point) or isinstance(value, wx.Position) or isinstance(value, wx.Size):
            value = list(value)
        if self.properties[key] != value:
            self.properties[key] = value
            for callback in self.propertyListeners:
                callback(self, key)
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

    def SendMessage(self, message):
        if self.runner:
            self.runner.RunHandler(self, "OnMessage", None, message)

    def Show(self, show=True):
        self.SetProperty("hidden", not show)

    def Hide(self, hide=True):
        self.SetProperty("hidden", hide)

    def GetSize(self): return list(self.GetProperty("size"))
    def SetSize(self, size): self.SetProperty("size", size)

    def GetPosition(self): return self.GetProperty("position")
    def SetPosition(self, pos): self.SetProperty("position", pos)
    def MoveBy(self, delta):
        pos = self.GetProperty("position")
        self.SetProperty("position", (pos[0]+delta[0], pos[1]+delta[1]))

    def IsTouching(self, model): return self.GetFrame().Intersects(model.GetFrame())
    def IsTouchingEdge(self, model):
        sf = self.GetFrame() # self frame
        f = model.GetFrame() # other frame
        top = wx.Rect(f.Left, f.Top, f.Width, 1)
        bottom = wx.Rect(f.Left, f.Bottom, f.Width, 1)
        left = wx.Rect(f.Left, f.Top, 1, f.Height)
        right = wx.Rect(f.Right, f.Top, 1, f.Height)
        if sf.Intersects(top): return "Top"
        if sf.Intersects(bottom): return "Bottom"
        if sf.Intersects(left): return "Left"
        if sf.Intersects(right): return "Right"
        return False

    def DeduplicateName(self, name, existingNames):
        existingNames.extend(["card", "self", "key", "mouseX",  "mouseY", "message"]) # disallow globals
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


class MoveUiViewCommand(Command):
    uiView = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]
        self.delta = args[5]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        pos = self.viewModel.GetProperty("position")
        self.viewModel.SetProperty("position", (pos[0]+self.delta[0], pos[1]+self.delta[1]))
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        pos = self.viewModel.GetProperty("position")
        self.viewModel.SetProperty("position", (pos[0]-self.delta[0], pos[1]-self.delta[1]))
        return True


class ResizeUiViewCommand(Command):
    uiView = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.cardIndex = args[3]
        self.viewModel = args[4]
        self.delta = args[5]

    def Do(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        viewSize = self.viewModel.GetProperty("size")
        self.viewModel.SetProperty("size", (viewSize[0]+self.delta[0], viewSize[1]+self.delta[1]))
        return True

    def Undo(self):
        self.stackView.LoadCardAtIndex(self.cardIndex)
        viewSize = self.viewModel.GetProperty("size")
        self.viewModel.SetProperty("size", (viewSize[0]-self.delta[0], viewSize[1]-self.delta[1]))
        return True
