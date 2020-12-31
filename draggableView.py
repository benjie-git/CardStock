#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx

class DraggableView(wx.Window):
    def __init__(self, editing, **kwargs):
        wx.Window.__init__(self, **kwargs)
        self.child = None
        self.type = None
        self.handlers = {"onClick":'print("UI element clicked!")'}
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

    def GetData(self):
        return {"type":self.type,
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
        # event.StopPropagation()
        event.Skip()

    def onDown(self, event):
        self.child.CaptureMouse()
        self.GetParent().SelectUIView(self)
        x, y = self.GetParent().ScreenToClient(self.ClientToScreen(event.GetPosition()))
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))

    def onMove(self, event):
        if event.Dragging():
            x, y = self.GetParent().ScreenToClient(self.ClientToScreen(event.GetPosition()))
            fp = (x-self.delta[0], y-self.delta[1])
            self.Move(fp)

    def onRelease(self, event):
        if self.child.HasCapture():
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
        dragButton = wx.Button(parent=self, id=-1, label="Button")
        self.SetChildView(dragButton)
        self.properties = {"title":"Button"}
        if self.isEditing:
            self.child.Bind(wx.EVT_BUTTON, self.skipEvent)


class DraggableTextField(DraggableView):
    def __init__(self, editing, **kwargs):
        DraggableView.__init__(self, editing, **kwargs)
        self.type = "textfield"
        dragText = wx.TextCtrl(parent=self, id=-1, value="Text")
        self.SetChildView(dragText)
        self.properties = {"text":"text"}
        if self.isEditing:
            dragText.SetEditable(False)
