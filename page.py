# page.py

"""
This module contains the PageWindow class which is a window that you
can do simple drawings upon. and add Buttons and TextFields to.
"""


import wx
from wx.lib.docview import CommandProcessor, Command
import sys
import json
from runner import Runner
from uiViews import UiButton, UiTextField, UiPage, UiView

# ----------------------------------------------------------------------

class PageWindow(wx.Window):
    menuColours = { 100 : 'White',
                    101 : 'Yellow',
                    102 : 'Red',
                    103 : 'Green',
                    104 : 'Blue',
                    105 : 'Purple',
                    106 : 'Brown',
                    107 : 'Aquamarine',
                    108 : 'Forest Green',
                    109 : 'Light Blue',
                    110 : 'Goldenrod',
                    111 : 'Cyan',
                    112 : 'Orange',
                    113 : 'Black',
                    114 : 'Dark Grey',
                    115 : 'Light Grey',
                    }
    maxThickness = 16

    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour("WHITE")
        self.listeners = []
        self.shapes = []
        self.designer = None
        self.command_processor = CommandProcessor()
        self.isEditing = False
        self.pos = wx.Point(0,0)
        self.isInDrawingMode = False
        self.isDrawing = False
        self.thickness = 4
        self.SetColour("Black")
        self.runner = None
        # self.MakeMenu()

        self.uiViews = []
        self.uiPage = UiPage(self)
        self.uiViews.append(self.uiPage)
        self.timer = None

        self.selectedView = None

        self.InitBuffer()

        self.UpdateCursor()

        # hook some mouse events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        # if editing:
        #     self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)

        # the view resize event and idle events for managing the buffer
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # and the refresh event
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # When the window is destroyed, clean up resources.
        self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)

    def SetEditing(self, editing):
        self.isEditing = editing
        for ui in self.uiViews:
            ui.SetEditing(editing)
        if not editing:
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.uiPage.OnIdle, self.timer)
            self.timer.Start(100)

    def UpdateCursor(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL if self.isInDrawingMode else wx.CURSOR_HAND))

    def SetDrawingMode(self, drawMode):
        self.isInDrawingMode = drawMode
        self.UpdateCursor()

    def ClearAll(self):
        self.SetLinesData([])
        self.SelectUiView(None)

        for ui in self.uiViews.copy():
            if ui.type != "page":
                self.uiViews.remove(ui)
                ui.DestroyView()
            else:
                for k,v in ui.GetHandlers().items():
                    ui.SetHandler(k,"")

    def GetData(self):
        data = {}
        data["shapes"] = self.GetShapesData()
        data["uiviews"] = self.GetUiViewsData()
        #for d in data["uiviews"]:
        #    d["properties"].pop("id")

        return data

    def LoadFromData(self, data):
        self.ClearAll()
        self.SetLinesData(data["shapes"])
        self.SetUiViewsData(data["uiviews"])
        self.UpdateSelectedUiView()

    def SetDesigner(self, designer):
        self.designer = designer

    def Cleanup(self, evt):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu
        if self.timer:
            self.timer.Stop()
        if self.runner:
            self.runner.StopRunning()

    def InitBuffer(self):
        """Initialize the bitmap used for buffering the display."""
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(max(1,size.width), max(1,size.height))
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawShapes(dc)
        self.reInitBuffer = False

    def SetColour(self, colour):
        """Set a new colour and make a matching pen"""
        self.colour = colour
        self.pen = wx.Pen(self.colour, self.thickness, wx.PENSTYLE_SOLID)
        self.Notify()

    def SetThickness(self, num):
        """Set a new line thickness and make a matching pen"""
        self.thickness = num
        self.pen = wx.Pen(self.colour, self.thickness, wx.PENSTYLE_SOLID)
        self.Notify()

    def CopyView(self):
        if self.selectedView:
            clipdata = wx.CustomDataObject("org.pycard.view")
            data = bytes(json.dumps(self.selectedView.GetData()).encode('utf8'))
            clipdata.SetData(data)
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(clipdata)
            wx.TheClipboard.Close()

    def CutView(self):
        if self.selectedView:
            self.CopyView()
            v = self.selectedView
            command = RemoveUiViewCommand(True, "Cut", v, self)
            self.command_processor.Submit(command)

    def PasteView(self):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat("org.pycard.view")):
                    clipdata = wx.CustomDataObject("org.pycard.view")
                    if wx.TheClipboard.GetData(clipdata):
                        rawdata = clipdata.GetData()
                        data = json.loads(rawdata.tobytes().decode('utf8'))
                        data["properties"]["id"] = UiView.GetNextUiViewId()
                        uiView = self.AddUiViewFromData(data)
                        self.SelectUiView(uiView)
                wx.TheClipboard.Close()

    def AddUiViewOfType(self, viewType):
        if viewType == "button":
            command = AddUiViewCommand(True, 'Add Button', self, "button")
            self.command_processor.Submit(command)
        elif viewType == "textfield":
            command = AddUiViewCommand(True, 'Add TextField', self, "textfield")
            self.command_processor.Submit(command)
        uiView = self.uiViews[-1]
        self.SelectUiView(uiView)
        return uiView

    def AddUiViewOfTypeInternal(self, type):
        uiView = None
        if type == "button":
            uiView = UiButton(self)
        elif type == "textfield":
            uiView = UiTextField(self)

        if uiView:
            uiView.view.Center()
            self.uiViews.append(uiView)
            uiView.SetEditing(self.isEditing)
        return uiView

    def AddUiViewFromData(self, data):
        uiView = None

        data["properties"]["name"] = self.DeduplicateName(data["properties"]["name"])

        if data["type"] == "button":
            command = AddUiViewCommand(True, 'Add Button', self, "button", data)
            self.command_processor.Submit(command)
            uiView = self.uiViews[-1]
        elif data["type"] == "textfield":
            command = AddUiViewCommand(True, 'Add TextField', self, "textfield", data)
            self.command_processor.Submit(command)
            uiView = self.uiViews[-1]
        elif data["type"] == "page":
            uiView = self.uiPage
            uiView.SetData(data)
            self.uiViews.append(uiView)

        uiView.SetEditing(self.isEditing)
        return uiView

    def DeduplicateName(self, name, exclude=[]):
        names = [v.properties["name"] for v in self.uiViews]
        for n in exclude:
            names.remove(n)

        if name in names:
            name = name.rstrip("0123456789")
            if name[-1:] != "_":
                name = name + "_"
            name = self.GetNextAvailableNameForBase(name, exclude)
        return name

    def GetShapesData(self):
        return self.shapes[:]

    def SetLinesData(self, lines):
        self.shapes = lines[:]
        self.InitBuffer()
        self.Refresh()

    def GetUiViewsData(self):
        return [v.GetData() for v in self.uiViews]

    def SetUiViewsData(self, data):
        self.uiViews = []
        for v in data:
            self.AddUiViewFromData(v)

    def GetSelectedUiView(self):
        return self.selectedView

    def SelectUiView(self, view):
        if self.selectedView:
            self.selectedView.SetSelected(False)
        if view:
            view.SetSelected(True)
        self.selectedView = view
        if self.designer:
            self.designer.SetSelectedUiView(view)

    def UpdateSelectedUiView(self):
        if self.designer:
            self.designer.UpdateSelectedUiView()

    def GetNextAvailableNameForBase(self, base, exclude=[]):
        names = [ui.GetProperty("name") for ui in self.uiViews]
        for n in exclude:
            names.remove(n)
        i = 1
        while True:
            name = base+str(i)
            if name not in names:
                return name
            i += 1

    def GetUiViewById(self, viewId):
        for ui in self.uiViews:
            if ui.GetProperty("id") == viewId:
                return ui
        return None

    def RemoveUiViewById(self, viewId):
        for ui in self.uiViews.copy():
            if ui.GetProperty("id") == viewId:
                if self.selectedView == ui:
                    self.SelectUiView(None)
                self.uiViews.remove(ui)
                ui.DestroyView()
                return

    def OnMouseDown(self, event):
        """called when the left mouse button is pressed"""
        if self.isEditing:
            if self.isInDrawingMode:
                self.curLine = []
                self.pos = event.GetPosition()
                coords = (self.pos.x, self.pos.y)
                self.curLine.append(coords)
                self.isDrawing = True
                self.CaptureMouse()
            else:
                self.SelectUiView(None)
        else:
            event.Skip()

    def OnMouseUp(self, event):
        """called when the left mouse button is released"""
        if self.isEditing:
            if self.HasCapture():
                command = AddLineCommand(True, 'Add Line', self,
                                         ("pen", self.colour, self.thickness, self.curLine) )
                self.command_processor.Submit(command)
                self.curLine = []
                self.isDrawing = False
                self.ReleaseMouse()
        else:
            event.Skip()

    def OnMouseMove(self, event):
        """
        Called when the mouse is in motion.  If the left button is
        dragging then draw a line from the last event position to the
        current one.  Save the coordinants for redraws.
        """
        if self.isEditing:
            if self.isDrawing and event.Dragging() and event.LeftIsDown():
                dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
                dc.SetPen(self.pen)
                pos = event.GetPosition()
                coords = (pos.x, pos.y)
                self.curLine.append(coords)
                dc.DrawLine(*(self.pos.x, self.pos.y, pos.x, pos.y))
                self.pos = pos
        else:
            event.Skip()

    def OnSize(self, event):
        """
        Called when the window is resized.  We set a flag so the idle
        handler will resize the buffer.
        """
        self.reInitBuffer = True
        event.Skip()

    def OnIdle(self, event):
        """
        If the size was changed then resize the bitmap used for double
        buffering to match the window size.  We do it in Idle time so
        there is only one refresh after resizing is done, not lots while
        it is happening.
        """
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)
        event.Skip()

    def OnPaint(self, event):
        """
        Called when the window is exposed.
        """
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer)

    def DrawShapes(self, dc):
        """
        Redraws all the shapes that have been drawn already.
        """
        for type, colour, thickness, line in self.shapes:
            pen = wx.Pen(colour, thickness, wx.PENSTYLE_SOLID)
            dc.SetPen(pen)

            lastPos = None
            if type == "pen":
                for coords in line:
                    if lastPos:
                        dc.DrawLine(*(lastPos[0], lastPos[1], coords[0], coords[1]))
                    lastPos = coords

    # Event handlers for the popup menu, uses the event ID to determine
    # the colour or the thickness to set.
    def OnMenuSetColour(self, event):
        self.SetColour(self.menuColours[event.GetId()])

    def OnMenuSetThickness(self, event):
        self.SetThickness(event.GetId())

    def Undo(self):
        self.command_processor.Undo()
        self.InitBuffer()
        self.Refresh()

    def Redo(self):
        self.command_processor.Redo()
        self.InitBuffer()
        self.Refresh()

    # Observer pattern.  Listeners are registered and then notified
    # whenever doodle settings change.
    def AddListener(self, listener):
        self.listeners.append(listener)

    def Notify(self):
        for other in self.listeners:
            other.UpdateLine(self.colour, self.thickness)


class AddLineCommand(Command):
    parent = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.parent = args[2]
        self.line = args[3]

    def Do(self):
        self.parent.shapes.append(self.line)
        return True

    def Undo(self):
        if len(self.parent.shapes):
            self.parent.shapes.pop();
        return True


class AddUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.page = args[2]
        self.viewType = args[3]
        self.viewData = args[4] if len(args)>4 else None
        self.viewId = None
        self.uiView = None

    def Do(self):
        self.uiView = self.page.AddUiViewOfTypeInternal(self.viewType)
        if self.viewData:
            self.uiView.SetData(self.viewData)
        if not self.viewId:
            self.viewId = self.uiView.GetProperty("id")
        else:
            self.uiView.SetProperty("id", self.viewId)
        return True

    def Undo(self):
        self.page.RemoveUiViewById(self.viewId)
        self.uiView = None
        return True


class RemoveUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.uiView = args[2]
        self.page = args[3]
        self.viewType = self.uiView.type
        self.viewData = self.uiView.GetData()
        self.viewId = self.uiView.GetProperty("id")

    def Do(self):
        self.page.RemoveUiViewById(self.viewId)
        self.uiView = None
        return True

    def Undo(self):
        self.uiView = self.page.AddUiViewOfTypeInternal(self.viewType)
        self.uiView.SetData(self.viewData)
        return True
