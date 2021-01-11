#!/usr/bin/python
# stackWindow.py

"""
This module contains the StackWindow class which is a window that you
can do simple drawings upon. and add Buttons and TextFields to.
"""


import wx
from wx.lib.docview import CommandProcessor, Command
import json
from stack import StackModel
from uiPage import UiPage, PageModel
from uiButton import UiButton
from uiTextField import UiTextField
from uiTextLabel import UiTextLabel
from uiImage import UiImage

# ----------------------------------------------------------------------

class StackWindow(wx.Window):
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

    def __init__(self, parent, ID, stackModel):
        wx.Window.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.WANTS_CHARS)
        self.SetBackgroundColour("WHITE")
        self.listeners = []
        self.designer = None
        self.command_processor = CommandProcessor()
        self.pos = wx.Point(0,0)
        self.isInDrawingMode = False
        self.isDrawing = False
        self.thickness = 4
        self.colour = None
        self.pen = None
        self.SetColour("Black")
        self.runner = None
        self.timer = None

        if not stackModel:
            stackModel = StackModel()
            stackModel.AddPageModel(PageModel())

        self.stackModel = stackModel
        self.selectedView = None
        self.LoadCardAtIndex(0)

        self.uiPage.model.SetDirty(False)
        self.command_processor.ClearCommands()

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

    def Cleanup(self, evt):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu
        if self.timer:
            self.timer.Stop()
        if self.runner:
            self.runner.StopRunning()

    def SetEditing(self, editing):
        self.uiPage.SetEditing(editing)
        for ui in self.uiViews:
            ui.SetEditing(editing)
        if not editing:
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.uiPage.OnIdle, self.timer)
            self.timer.Start(50)

    def UpdateCursor(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL if self.isInDrawingMode else wx.CURSOR_HAND))

    def SetDrawingMode(self, drawMode):
        self.isInDrawingMode = drawMode
        self.UpdateCursor()

    def ClearAllViews(self):
        self.SelectUiView(None)
        for ui in self.uiViews.copy():
            if ui.model.type != "page":
                ui.model.RemovePropertyListener(self.OnPropertyChanged)
                self.uiViews.remove(ui)
                self.uiPage.model.RemoveChild(ui.model)
                ui.DestroyView()

    def CreateViews(self, pageModel):
        self.uiPage = UiPage(self, pageModel)
        self.uiViews = []
        for m in pageModel.childModels:
            self.AddUiViewFromModel(m)

    def SetStackModel(self, model):
        self.ClearAllViews()
        self.stackModel = model
        self.LoadCardAtIndex(0)
        self.command_processor.ClearCommands()
        self.stackModel.SetDirty(False)

    def LoadCardAtIndex(self, index):
        self.pageIndex = index
        pageModel = self.stackModel.GetPageModel(index)
        self.CreateViews(pageModel)
        self.SelectUiView(self.uiPage)
        pageModel.AddPropertyListener(self.OnPropertyChanged)
        self.InitBuffer()

    def SetDesigner(self, designer):
        self.designer = designer

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
        clipData = wx.CustomDataObject("org.cardstock.models")
        list = [self.selectedView.model.GetData()]
        data = bytes(json.dumps(list).encode('utf8'))
        clipData.SetData(data)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipData)
        wx.TheClipboard.Close()

    def CutView(self):
        if self.selectedView != self.uiPage:
            self.CopyView()
            v = self.selectedView
            command = RemoveUiViewCommand(True, "Cut", v.model, self)
            self.command_processor.Submit(command)

    def PasteView(self):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            if wx.TheClipboard.Open():
                if wx.TheClipboard.IsSupported(wx.DataFormat("org.cardstock.models")):
                    clipData = wx.CustomDataObject("org.cardstock.models")
                    if wx.TheClipboard.GetData(clipData):
                        rawdata = clipData.GetData()
                        list = json.loads(rawdata.tobytes().decode('utf8'))
                        uiView = None
                        for dict in list:
                            model = PageModel.ModelFromData(dict)
                            if model.type == "page":
                                for m in model.childModels:
                                    uiView = self.AddUiViewFromModel(m)
                            else:
                                uiView = self.AddUiViewFromModel(model)
                        if uiView:
                            self.SelectUiView(uiView)
                wx.TheClipboard.Close()

    def AddUiViewOfType(self, viewType):
        if viewType == "button":
            command = AddUiViewCommand(True, 'Add Button', self, "button")
        elif viewType == "textfield":
            command = AddUiViewCommand(True, 'Add TextField', self, "textfield")
        elif viewType == "textlabel":
            command = AddUiViewCommand(True, 'Add TextLabel', self, "textlabel")
        elif viewType == "image":
            command = AddUiViewCommand(True, 'Add Image', self, "image")

        self.command_processor.Submit(command)
        uiView = self.uiViews[-1]
        self.SelectUiView(uiView)
        return uiView

    def AddUiViewInternal(self, type, model=None):
        uiView = None
        if type == "button":
            uiView = UiButton(self, model)
        elif type == "textfield":
            uiView = UiTextField(self, model)
        elif type == "textlabel":
            uiView = UiTextLabel(self, model)
        elif type == "image":
            uiView = UiImage(self, model)

        if uiView:
            if not model:
                uiView.view.Center()
                uiView.model.SetProperty("position", uiView.view.GetPosition())
                uiView.model.SetProperty("size", uiView.view.GetSize())
            self.uiViews.append(uiView)
            if not uiView.model in self.uiPage.model.childModels:
                self.uiPage.model.AddChild(uiView.model)
            uiView.model.AddPropertyListener(self.OnPropertyChanged)
            uiView.SetEditing(self.uiPage.isEditing)
        return uiView

    def AddUiViewFromModel(self, model):
        uiView = None

        if not model in self.uiPage.model.childModels:
            model.SetProperty("name", self.uiPage.model.DeduplicateName(model.GetProperty("name")))

        if model.GetType() == "button":
            command = AddUiViewCommand(True, 'Add Button', self, "button", model)
        elif model.GetType() == "textfield":
            command = AddUiViewCommand(True, 'Add TextField', self, "textfield", model)
        elif model.GetType() == "textlabel":
            command = AddUiViewCommand(True, 'Add TextLabel', self, "textlabel", model)
        elif model.GetType() == "image":
            command = AddUiViewCommand(True, 'Add Image', self, "image", model)

        self.command_processor.Submit(command)
        uiView = self.uiViews[-1]
        if uiView:
            uiView.SetEditing(self.uiPage.isEditing)
        return uiView

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

    def OnPropertyChanged(self, model, key):
        uiView = self.GetUiViewByModel(model)
        if self.designer:
            self.designer.cPanel.UpdatedProperty(uiView, key)

    def UpdateSelectedUiView(self):
        if self.designer:
            self.designer.UpdateSelectedUiView()

    def GetUiViewByModel(self, model):
        for ui in self.uiViews:
            if ui.model == model:
                return ui
        return None

    def RemoveUiViewByModel(self, viewModel):
        for ui in self.uiViews.copy():
            if ui.model == viewModel:
                if self.selectedView == ui:
                    self.SelectUiView(self.uiPage)
                ui.model.RemoveAllPropertyListeners()
                self.uiViews.remove(ui)
                self.uiPage.model.RemoveChild(ui.model)
                ui.DestroyView()
                return

    def OnMouseDown(self, event):
        """called when the left mouse button is pressed"""
        if self.uiPage.isEditing:
            if self.isInDrawingMode:
                self.curLine = []
                self.pos = event.GetPosition()
                coords = (self.pos.x, self.pos.y)
                self.curLine.append(coords)
                self.isDrawing = True
                self.CaptureMouse()
            else:
                self.SelectUiView(self.uiPage)
        else:
            event.Skip()

    def OnMouseMove(self, event):
        """
        Called when the mouse is in motion.  If the left button is
        dragging then draw a line from the last event position to the
        current one.  Save the coordinants for redraws.
        """
        if self.uiPage.isEditing:
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

    def OnMouseUp(self, event):
        """called when the left mouse button is released"""
        if self.uiPage.isEditing:
            if self.HasCapture() and self.isInDrawingMode:
                command = AddLineCommand(True, 'Add Line', self,
                                         ("pen", self.colour, self.thickness, self.curLine) )
                self.command_processor.Submit(command)
                self.curLine = []
                self.isDrawing = False
                self.ReleaseMouse()
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
        for type, colour, thickness, line in self.uiPage.model.shapes:
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
        self.stackView = args[2]
        self.line = args[3]

    def Do(self):
        self.stackView.uiPage.model.shapes.append(self.line)
        return True

    def Undo(self):
        if len(self.stackView.uiPage.model.shapes):
            self.stackView.uiPage.model.shapes.pop()
        return True


class AddUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.stackView = args[2]
        self.viewType = args[3]
        self.model = args[4] if len(args)>4 else None

    def Do(self):
        uiView = self.stackView.AddUiViewInternal(self.viewType, self.model)
        if not self.model:
            self.model = uiView.model
        return True

    def Undo(self):
        self.stackView.RemoveUiViewByModel(self.model)
        return True


class RemoveUiViewCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.viewModel = args[2]
        self.stackView = args[3]

    def Do(self):
        self.stackView.RemoveUiViewByModel(self.viewModel)
        return True

    def Undo(self):
        self.stackView.AddUiViewInternal(self.viewModel.type, self.viewModel)
        return True
