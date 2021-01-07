#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from wx.lib.docview import Command


class UiView(object):
    def __init__(self, page, model, view):
        super().__init__()
        self.page = page
        self.view = view

        self.model = model
        self.model.AddPropertyListener(self.OnPropertyChanged)

        mSize = self.model.GetProperty("size")
        if mSize[0] > 0 and mSize[1] > 0:
            self.view.SetSize(mSize)
            self.view.SetPosition(self.model.GetProperty("position"))

        self.lastEditedHandler = None
        self.delta = ((0, 0))
        self.minSize = (20,20)
        self.isEditing = False
        self.isSelected = False
        self.view.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.view.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
        self.view.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.view.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.view.Bind(wx.EVT_SIZE, self.OnResize)
        if self.model.type != "page":
            self.view.Bind(wx.EVT_MOTION, self.page.uiPage.OnMouseMove)
        self.view.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)

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

    def __del__(self):
        self.model.RemoveAllPropertyListeners()

    def OnPropertyChanged(self, model, key):
        if key == "size":
            self.view.SetSize(self.model.GetProperty("size"))
        elif key == "position":
            self.view.SetPosition(self.model.GetProperty("position"))

    def OnResize(self, event):
        setW, setH = self.view.GetSize()
        w, h = (setW, setH)
        if w < 20:
            w = 20
        if h < 20:
            h = 20
        if w != setW or h != setH:
            self.view.SetSize(w, h)
        self.selectionBox.SetSize(w, h)
        x,y = self.view.GetPosition()
        self.resizeBox.SetRect((w-10, h-10, 10, 10))

    def DestroyView(self):
        self.selectionBox.Destroy()
        self.resizeBox.Destroy()
        self.view.Destroy()

    def SetEditing(self, editing):
        self.isEditing = editing
        self.SetSelected(False)

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        self.isSelected = selected
        self.selectionBox.Show(selected)
        self.resizeBox.Show(selected)
        self.view.Refresh()
        self.view.Update()

    def OnMouseDown(self, event):
        if self.model.type != "page" and self.isEditing:
            self.view.CaptureMouse()
            x, y = self.page.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
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

            self.page.SelectUiView(self)
        else:
            if "OnMouseDown" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnMouseDown", event)
            event.Skip()

    def OnMouseMove(self, event):
        if self.model.type != "page" and self.isEditing and event.Dragging():
            x, y = self.page.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
            if not self.isResizing:
                fp = (x - self.delta[0], y - self.delta[1])
                self.view.Move(fp)
                self.model.SetProperty("position", self.view.GetPosition())
            else:
                offset = (x-self.origMousePos[0], y-self.origMousePos[1])
                self.view.SetSize(self.origSize[0]+offset[0], self.origSize[1]+offset[1])
                self.model.SetProperty("size", self.view.GetSize())
        elif not self.isEditing:
            if "OnMouseMove" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnMouseMove", event)
        event.Skip()

    def OnMouseUp(self, event):
        if self.model.type != "page" and self.isEditing and self.view.HasCapture():
            self.view.ReleaseMouse()
            if not self.isResizing:
                endx, endy = self.view.GetPosition()
                offset = (endx-self.moveOrigin[0], endy-self.moveOrigin[1])
                if offset != (0, 0):
                    command = MoveUiViewCommand(True, 'Move', self.page, self, offset)
                    self.view.SetPosition(self.moveOrigin)
                    self.page.command_processor.Submit(command)
            else:
                endw, endh = self.view.GetSize()
                offset = (endw-self.origSize[0], endh-self.origSize[1])
                if offset != (0, 0):
                    command = ResizeUiViewCommand(True, 'Resize', self.page, self, offset)
                    self.view.SetSize(self.origSize)
                    self.page.command_processor.Submit(command)

            self.page.SetFocus()
        elif not self.isEditing:
            if "OnMouseUp" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnMouseUp", event)
            event.Skip()

    def OnMouseEnter(self, event):
        if not self.isEditing:
            if "OnMouseEnter" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnMouseEnter", event)
            event.Skip()

    def OnMouseExit(self, event):
        if not self.isEditing:
            if "OnMouseExit" in self.model.handlers:
                self.model.runner.RunHandler(self, "OnMouseExit", event)
            event.Skip()

    def OnPaintSelectionBox(self, event):
        dc = wx.PaintDC(self.selectionBox)
        dc.SetPen(wx.Pen('Blue', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle((1, 1), (self.selectionBox.GetSize()[0]-2, self.selectionBox.GetSize()[1]-2))

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
                         "OnMessage": ""
                         }
        self.properties = {"name": "",
                           "size": (0,0),
                           "position": (0,0)
                           }
        self.propertyKeys = ["name", "position", "size"]

        self.propertyListeners = []

        self.runner = None

    def GetType(self):
        return self.type

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
        self.properties[key] = value
        for callback in self.propertyListeners:
            callback(self, key)

    def SetHandler(self, key, value):
        self.handlers[key] = value

    def SendMessage(self, message):
        if self.runner:
            self.runner.RunHandler(self, "OnMessage", None, message)

    def GetSize(self): return list(self.GetProperty("size"))
    def SetSize(self, size): self.SetProperty("size", size)
    def GetPosition(self): return self.GetProperty("position")
    def SetPosition(self, pos): self.SetProperty("position", pos)
    def GetPosition(self): return self.GetProperty("position")
    def MoveTo(self, pos): self.SetProperty("position", pos)


class MoveUiViewCommand(Command):
    uiView = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.page = args[2]
        self.uiView = args[3]
        self.delta = args[4]
        self.viewModel = self.uiView.model

    def Do(self):
        uiView = self.page.GetUiViewByModel(self.viewModel)
        pos = uiView.view.GetPosition()
        uiView.view.SetPosition((pos[0]+self.delta[0], pos[1]+self.delta[1]))
        return True

    def Undo(self):
        uiView = self.page.GetUiViewByModel(self.viewModel)
        pos = uiView.view.GetPosition()
        uiView.view.SetPosition((pos[0]-self.delta[0], pos[1]-self.delta[1]))
        return True


class ResizeUiViewCommand(Command):
    uiView = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.page = args[2]
        self.uiView = args[3]
        self.delta = args[4]
        self.viewModel = self.uiView.model

    def Do(self):
        uiView = self.page.GetUiViewByModel(self.viewModel)
        viewSize = uiView.view.GetSize()
        uiView.view.SetSize((viewSize[0]+self.delta[0], viewSize[1]+self.delta[1]))
        return True

    def Undo(self):
        uiView = self.page.GetUiViewByModel(self.viewModel)
        viewSize = uiView.view.GetSize()
        uiView.view.SetSize((viewSize[0]-self.delta[0], viewSize[1]-self.delta[1]))
        return True
