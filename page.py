# page.py

"""
This module contains the PageWindow class which is a window that you
can do simple drawings upon. and add Buttons and TextFields to.
"""


import wx
import sys
from six.moves import cPickle as pickle
from draggableView import DraggableButton,DraggableTextField

#----------------------------------------------------------------------

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


    def __init__(self, parent, ID, editing):
        wx.Window.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour("WHITE")
        self.listeners = []
        self.thickness = 4
        self.SetColour("Black")
        self.lines = []
        self.designer = None
        self.isDrawing = False
        self.isEditing = editing
        self.pos = wx.Point(0,0)
        self.MakeMenu()

        self.uiViews = []

        self.selectedView = None
        self.handlers = {"onOpen":'print("Page Opened")'}

        self.InitBuffer()

        self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

        # hook some mouse events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        # the window resize event and idle events for managing the buffer
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # and the refresh event
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # When the window is destroyed, clean up resources.
        self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)


    def ReadFile(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            self.SetLinesData(data["lines"])
            self.SetUIViewsData(data["uiviews"])
            self.SetHandlersData(data["handlers"])
        except pickle.UnpicklingError:
            wx.MessageBox("%s is not a page file." %filename,
                          "oops!", style=wx.OK | wx.ICON_EXCLAMATION)


    def SetDesigner(self, designer):
        self.designer = designer


    def Cleanup(self, evt):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu


    def InitBuffer(self):
        """Initialize the bitmap used for buffering the display."""
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(max(1,size.width), max(1,size.height))
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawLines(dc)
        self.reInitBuffer = False


    def SetColour(self, colour):
        """Set a new colour and make a matching pen"""
        self.colour = colour
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.Notify()


    def SetThickness(self, num):
        """Set a new line thickness and make a matching pen"""
        self.thickness = num
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.Notify()


    def AddUiViewOfType(self, viewType):
        dragView = None
        if viewType == "button":
            dragView = DraggableButton(self.isEditing, parent=self, id=-1)
        elif viewType == "text":
            dragView = DraggableTextField(self.isEditing, parent=self, id=-1)
        dragView.Center()
        self.uiViews.append(dragView)


    def AddUiViewFromData(self, data):
        dragView = None
        if data["type"] == "button":
            dragView = DraggableButton(self.isEditing, parent=self, id=-1)
        elif data["type"] == "textfield":
            dragView = DraggableTextField(self.isEditing, parent=self, id=-1)
        dragView.SetData(data)
        self.uiViews.append(dragView)


    def GetLinesData(self):
        return self.lines[:]

    def SetLinesData(self, lines):
        self.lines = lines[:]
        self.InitBuffer()
        self.Refresh()

    def GetUIViewsData(self):
        return [v.GetData() for v in self.uiViews]

    def SetUIViewsData(self, data):
        self.uiViews = []
        for v in data:
            self.AddUiViewFromData(v)

    def GetHandlersData(self):
        return self.handlers

    def SetHandlersData(self, data):
        self.handlers = data

    def MakeMenu(self):
        """Make a menu that can be popped up later"""
        menu = wx.Menu()
        for k in sorted(self.menuColours):
            text = self.menuColours[k]
            menu.Append(k, text, kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuSetColour, id=100, id2=200)
        self.Bind(wx.EVT_UPDATE_UI_RANGE, self.OnCheckMenuColours, id=100, id2=200)
        menu.Break()

        for x in range(1, self.maxThickness+1):
            menu.Append(x, str(x), kind=wx.ITEM_CHECK)

        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuSetThickness, id=1, id2=self.maxThickness)
        self.Bind(wx.EVT_UPDATE_UI_RANGE, self.OnCheckMenuThickness, id=1, id2=self.maxThickness)
        self.menu = menu


    # These two event handlers are called before the menu is displayed
    # to determine which items should be checked.
    def OnCheckMenuColours(self, event):
        text = self.menuColours[event.GetId()]
        if text == self.colour:
            event.Check(True)
            event.SetText(text.upper())
        else:
            event.Check(False)
            event.SetText(text)

    def OnCheckMenuThickness(self, event):
        if event.GetId() == self.thickness:
            event.Check(True)
        else:
            event.Check(False)


    def OnLeftDown(self, event):
        """called when the left mouse button is pressed"""
        self.curLine = []
        self.pos = event.GetPosition()
        self.isDrawing = True
        self.CaptureMouse()


    def OnLeftUp(self, event):
        """called when the left mouse button is released"""
        if self.HasCapture():
            self.lines.append( (self.colour, self.thickness, self.curLine) )
            self.curLine = []
            self.isDrawing = False
            self.ReleaseMouse()


    def OnRightUp(self, event):
        """called when the right mouse button is released, will popup the menu"""
        self.PopupMenu(self.menu)


    def GetSelectedUIView(self):
        return self.selectedView


    def SelectUIView(self, view):
        if self.selectedView:
            self.selectedView.SetSelected(False)
        view.SetSelected(True)
        self.selectedView = view
        self.designer.SetSelectedUIView(view)


    def OnMotion(self, event):
        """
        Called when the mouse is in motion.  If the left button is
        dragging then draw a line from the last event position to the
        current one.  Save the coordinants for redraws.
        """
        if self.isDrawing and event.Dragging() and event.LeftIsDown():
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            dc.SetPen(self.pen)
            pos = event.GetPosition()
            coords = (self.pos.x, self.pos.y, pos.x, pos.y)
            self.curLine.append(coords)
            dc.DrawLine(*coords)
            self.pos = pos


    def OnSize(self, event):
        """
        Called when the window is resized.  We set a flag so the idle
        handler will resize the buffer.
        """
        self.reInitBuffer = True


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


    def OnPaint(self, event):
        """
        Called when the window is exposed.
        """
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer)


    def DrawLines(self, dc):
        """
        Redraws all the lines that have been drawn already.
        """
        for colour, thickness, line in self.lines:
            pen = wx.Pen(colour, thickness, wx.SOLID)
            dc.SetPen(pen)
            for coords in line:
                dc.DrawLine(*coords)


    # Event handlers for the popup menu, uses the event ID to determine
    # the colour or the thickness to set.
    def OnMenuSetColour(self, event):
        self.SetColour(self.menuColours[event.GetId()])

    def OnMenuSetThickness(self, event):
        self.SetThickness(event.GetId())


    # Observer pattern.  Listeners are registered and then notified
    # whenever doodle settings change.
    def AddListener(self, listener):
        self.listeners.append(listener)

    def Notify(self):
        for other in self.listeners:
            other.Update(self.colour, self.thickness)


#----------------------------------------------------------------------

class PageFrame(wx.Frame):
    def __init__(self, parent, editing):
        wx.Frame.__init__(self, parent, -1, "Page", size=(800,600),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.page = PageWindow(self, -1, editing)

#----------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.App()
    frame = PageFrame(None, False)
    if len(sys.argv) > 1:
        frame.page.ReadFile(sys.argv[1])
    frame.Show(True)
    app.MainLoop()

