#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from wx.lib.docview import CommandProcessor, Command

class DraggableView(wx.Window):
    def __init__(self, editing, **kwargs):
        wx.Window.__init__(self, **kwargs)
        self.child = None
        self.type = None
        self.handlers = {"onClick":''}
        self.properties = {}
        self.delta = ((0, 0))
        self.isEditing = editing
        self.isSelected = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        if self.isEditing:
            self.Bind(wx.EVT_LEFT_DOWN, self.skipEvent)
            # self.Bind(wx.EVT_MOTION, self.skipEvent)
            # self.Bind(wx.EVT_LEFT_UP, self.skipEvent)

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        self.isSelected = selected
        self.Refresh()
        self.Update()

    def GetHandler(self, name):
        return self.handlers[name]

    def SetHandler(self, name, handlerStr):
        self.handlers[name] = handlerStr

    def GetProperty(self, name):
        return self.properties[name]

    def SetProperty(self, name, value):
        self.properties[name] = value

    def GetData(self):
        return {"type":self.type,
                "id":self.GetId(),
                "frame":(self.GetRect()),
                "handlers":self.handlers,
                "properties":self.properties}

    def SetData(self, data):
        self.SetRect(data["frame"])
        self.handlers = data["handlers"]
        self.properties = data["properties"]

    def SetChildView(self, view):
        self.child = view
        self.SetSize(view.GetSize()[0]+4, view.GetSize()[1]+4)
        self.child.Center()
        if self.isEditing:
            self.child.Bind(wx.EVT_LEFT_DOWN, self.onDown)
            self.child.Bind(wx.EVT_MOTION, self.onMove)
            self.child.Bind(wx.EVT_LEFT_UP, self.onRelease)
        if not self.isEditing:
            self.child.Bind(wx.EVT_BUTTON, self.onButton)

    def skipEvent(self, event):
        event.Skip()

    def onDown(self, event):
        self.child.CaptureMouse()
        self.GetParent().SelectUIView(self)
        x, y = self.GetParent().ScreenToClient(self.ClientToScreen(event.GetPosition()))
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.moveOrigin = (originx, originy)
        self.delta = ((dx, dy))

    def onMove(self, event):
        if event.Dragging():
            x, y = self.GetParent().ScreenToClient(self.ClientToScreen(event.GetPosition()))
            fp = (x-self.delta[0], y-self.delta[1])
            self.Move(fp)

    def onRelease(self, event):
        if self.child.HasCapture():
            endx, endy = self.GetPosition()
            command = MoveUIViewCommand(True, 'Move', self.GetParent(), self, (endx-self.moveOrigin[0], endy-self.moveOrigin[1]))
            self.SetPosition(self.moveOrigin)
            self.GetParent().command_processor.Submit(command)
            self.child.ReleaseMouse()

    def onButton(self, event):
        if self.handlers["onClick"]:
            exec(self.handlers["onClick"])

    def OnPaint(self, event):
        if self.isSelected:
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen('Blue', 2, wx.SOLID))
            #dc.SetBrush(wx.Brush('Blue', wx.SOLID))
            dc.DrawRectangle((1, 1), (self.GetSize()[0]-1, self.GetSize()[1]-1))


class DraggableButton(DraggableView):
    def __init__(self, editing, **kwargs):
        DraggableView.__init__(self, editing, **kwargs)
        self.type = "button"
        dragButton = wx.Button(parent=self, id=wx.ID_ANY, label="Button")
        self.SetChildView(dragButton)
        self.properties["title"] = "Button"
        if self.isEditing:
            self.child.Bind(wx.EVT_BUTTON, self.skipEvent)


class DraggableTextField(DraggableView):
    def __init__(self, editing, **kwargs):
        DraggableView.__init__(self, editing, **kwargs)
        self.type = "textfield"
        dragText = wx.TextCtrl(parent=self, id=wx.ID_ANY, value="Text")
        self.SetChildView(dragText)
        self.properties["text"] = "Text"
        if self.isEditing:
            dragText.SetEditable(False)


class MoveUIViewCommand(Command):
    dragView = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.parent = args[2]
        self.dragView = args[3]
        self.delta = args[4]
        self.viewId = self.dragView.GetId()

    def Do(self):
        view = self.parent.GetUIViewById(self.viewId)
        pos = view.GetPosition()
        view.SetPosition((pos[0]+self.delta[0],
                                   pos[1]+self.delta[1]))
        return True

    def Undo(self):
        view = self.parent.GetUIViewById(self.viewId)
        pos = view.GetPosition()
        view.SetPosition((pos[0]-self.delta[0],
                                   pos[1]-self.delta[1]))
        return True
