#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from wx.lib.docview import CommandProcessor, Command
import types

class DraggableView():
    def __init__(self, page, uiView):
        self.page = page
        self.view = uiView
        self.type = None
        self.handlers = {}
        self.properties = {}
        self.delta = ((0, 0))
        self.isEditing = False
        self.isSelected = False
        self.view.Bind(wx.EVT_LEFT_DOWN, self.OnDown)
        self.view.Bind(wx.EVT_MOTION, self.OnMove)
        self.view.Bind(wx.EVT_LEFT_UP, self.OnRelease)

        self.selectionBox = wx.Window(parent=self.view, id=wx.ID_ANY, pos=(0,0), size=self.view.GetSize(), style=0)
        self.selectionBox.Bind(wx.EVT_PAINT, self.OnPaintSelectionBox)
        self.selectionBox.SetBackgroundColour(None)
        self.selectionBox.Enable(False)
        self.selectionBox.Hide()

    def SetEditing(self, editing):
        self.isEditing = editing
        self.SetSelected(False)

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        self.isSelected = selected
        self.selectionBox.Show(selected)
        self.view.Refresh()
        self.view.Update()

    def GetHandlers(self):
        return self.handlers

    def GetHandler(self, name):
        if name in self.handlers:
            return self.handlers[name]
        return None

    def SetHandler(self, name, handlerStr):
        self.handlers[name] = handlerStr

    def GetProperty(self, name):
        return self.properties[name]

    def SetProperty(self, name, value):
        self.properties[name] = value

    def GetData(self):
        return {"type":self.type,
                "id":self.view.GetId(),
                "frame":(self.view.GetRect()),
                "handlers":self.handlers,
                "properties":self.properties}

    def SetData(self, data):
        self.view.SetRect(data["frame"])
        self.handlers = data["handlers"]
        self.properties = data["properties"]

    def OnDown(self, event):
        if self.isEditing:
            self.view.CaptureMouse()
            x, y = self.page.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
            originx, originy = self.view.GetPosition()
            dx = x - originx
            dy = y - originy
            self.moveOrigin = (originx, originy)
            self.delta = ((dx, dy))
            self.page.SelectUIView(self)
        else:
            event.Skip()

    def OnMove(self, event):
        if self.isEditing and event.Dragging():
            x, y = self.page.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
            fp = (x-self.delta[0], y-self.delta[1])
            self.view.Move(fp)

    def OnRelease(self, event):
        if self.isEditing and self.view.HasCapture():
            endx, endy = self.view.GetPosition()
            command = MoveUIViewCommand(True, 'Move', self.page, self, (endx-self.moveOrigin[0], endy-self.moveOrigin[1]))
            self.view.SetPosition(self.moveOrigin)
            self.page.command_processor.Submit(command)
            self.view.ReleaseMouse()

    def OnButton(self, event):
        if not self.isEditing:
            if "OnClick" in self.handlers:
                self.page.RunHandler(self, self.handlers["OnClick"])

    def OnPaintSelectionBox(self, event):
        dc = wx.PaintDC(self.selectionBox)
        dc.SetPen(wx.Pen('Blue', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle((1, 1), (self.selectionBox.GetSize()[0]-2, self.selectionBox.GetSize()[1]-2))


class DraggableButton(DraggableView):
    def __init__(self, page, viewId):
        button = wx.Button(parent=page, id=viewId, label="Button")
        DraggableView.__init__(self, page, button)
        self.type = "button"
        self.handlers["OnClick"] = ""
        self.handlers["OnIdle"] = ""
        self.properties["name"] = "button" + str(viewId-999)
        self.view.Bind(wx.EVT_BUTTON, self.OnButton)


class DraggableTextField(DraggableView):
    def __init__(self, page, viewId):
        field = wx.TextCtrl(parent=page, id=viewId, value="TextField")

        # Add easier methods to a new TextCtrl
        def SetText(self, text):
            self.ChangeValue(text)
        field.SetText = types.MethodType(SetText, field)

        def GetText(self):
            return self.GetValue()
        field.GetText = types.MethodType(GetText, field)

        DraggableView.__init__(self, page, field)
        self.type = "textfield"
        self.handlers["OnTextChanged"] = ""
        self.handlers["OnEnter"] = ""
        self.properties["name"] = "field" + str(viewId-999)

    def SetEditing(self, editing):
        DraggableView.SetEditing(self, editing)
        self.view.SetEditable(not editing)


class MoveUIViewCommand(Command):
    dragView = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.page = args[2]
        self.dragView = args[3]
        self.delta = args[4]
        self.viewId = self.dragView.view.GetId()

    def Do(self):
        uiView = self.page.GetUIViewById(self.viewId)
        pos = uiView.view.GetPosition()
        uiView.view.SetPosition((pos[0]+self.delta[0], pos[1]+self.delta[1]))
        return True

    def Undo(self):
        uiView = self.page.GetUIViewById(self.viewId)
        pos = uiView.view.GetPosition()
        uiView.view.SetPosition((pos[0]-self.delta[0], pos[1]-self.delta[1]))
        return True
