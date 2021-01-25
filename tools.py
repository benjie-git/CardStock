import wx
from commands import *
import math

class BaseTool(object):
    def __init__(self, stackView):
        super().__init__()
        self.stackView = stackView
        self.targetUi = None
        self.cursor = None
        self.name = ""

    @classmethod
    def ToolFromName(cls, name, stackView):
        if name == "hand":
            return HandTool(stackView)
        elif name == "button" or name == "field" or name == "label" or name == "image":
            return ViewTool(stackView, name)
        elif name == "pen":
            return PenTool(stackView)
        elif name == "rect" or name == "round_rect" or name == "oval" or name == "line":
            return ShapeTool(stackView, name)
        else:
            return HandTool(stackView)

    def GetCursor(self):
        return self.cursor

    def OnMouseDown(self, uiView, event):
        event.Skip()

    def OnMouseMove(self, uiView, event):
        event.Skip()

    def OnMouseUp(self, uiView, event):
        event.Skip()

    def OnKeyDown(self, uiView, event):
        event.Skip()

    def OnKeyUp(self, uiView, event):
        event.Skip()


class HandTool(BaseTool):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.cursor = None
        self.name = "hand"

    def OnMouseDown(self, uiView, event):
        skipSelect = False
        if uiView.parent == self.stackView.uiCard or not uiView.parent:
            # Clicked on a top-level uiView or the card itself
            self.targetUi = uiView
        else:
            # Clicked on a group's subview
            oldSelection = self.stackView.GetSelectedUiViews()
            while uiView.parent and uiView.parent.parent:
                if uiView.parent.isSelected or (len(oldSelection) == 1 and \
                                                oldSelection[0].parent == uiView.parent and \
                                                oldSelection[0] != uiView):
                    # If the parent or a sibling of this subview was already selected
                    self.stackView.SelectUiView(uiView)
                    skipSelect = True
                    break
                uiView = uiView.parent
            self.targetUi = uiView
            while self.targetUi.parent and self.targetUi.parent.model.type == "group":
                self.targetUi = self.targetUi.parent

        x, y = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        originx, originy = self.targetUi.view.GetPosition()
        dx = x - originx
        dy = y - originy
        self.moveOrigin = (originx, originy)
        self.origMousePos = (x, y)
        self.origSize = list(self.targetUi.view.GetSize())
        self.delta = ((dx, dy))

        rpx,rpy = self.targetUi.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        hackOffset = 5 if self.targetUi.model.type == "button" else 0  # Buttons are bigger than specified???
        if self.origSize[0] - rpx + hackOffset < 10 and self.origSize[1] - rpy + hackOffset < 10:
            self.isResizing = True
        else:
            self.isResizing = False

        if self.targetUi.model.type != "card" or self.isResizing:
            self.targetUi.view.CaptureMouse()

        if not skipSelect or self.isResizing:
            self.stackView.SelectUiView(self.targetUi, event.ShiftDown())

    def OnMouseMove(self, uiView, event):
        if self.targetUi and self.targetUi.view.HasCapture():
            x, y = self.stackView.ScreenToClient(self.targetUi.view.ClientToScreen(event.GetPosition()))
            if not self.isResizing:
                self.targetUi.model.SetProperty("position", [x - self.delta[0], y - self.delta[1]])
            else:
                offset = (x-self.origMousePos[0], y-self.origMousePos[1])
                self.targetUi.model.SetProperty("size", [self.origSize[0]+offset[0], self.origSize[1]+offset[1]])
        event.Skip()

    def OnMouseUp(self, uiView, event):
        if self.targetUi and self.targetUi.view.HasCapture():
            self.targetUi.view.ReleaseMouse()
            if not self.isResizing:
                endX, endY = self.targetUi.view.GetPosition()
                offset = (endX-self.moveOrigin[0], endY-self.moveOrigin[1])
                if offset != (0, 0):
                    command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, self.targetUi.model, offset)
                    self.targetUi.model.SetProperty("position", self.moveOrigin)
                    self.stackView.command_processor.Submit(command)
            else:
                endw, endh = self.targetUi.view.GetSize()
                offset = (endw-self.origSize[0], endh-self.origSize[1])
                if offset != (0, 0):
                    model = self.stackView.stackModel if self.targetUi.model.type == "card" else self.targetUi.model
                    command = ResizeUiViewCommand(True, 'Resize', self.stackView, self.stackView.cardIndex, model, offset)
                    self.targetUi.model.SetProperty("size", self.origSize)
                    self.stackView.command_processor.Submit(command)

            self.stackView.SetFocus()
            self.targetUi = None
        event.Skip()

    def OnKeyDown(self, uiViewIn, event):
        uiViews = []
        if uiViewIn and uiViewIn.model.type == "card":
            uiViews = self.stackView.GetSelectedUiViews()

        code = event.GetKeyCode()
        commands = []
        for uiView in uiViews:
            if uiView.model.type == "card":
                continue
            if uiView.parent and uiView.parent.model.type == "group":
                continue
            pos = wx.Point(uiView.model.GetProperty("position"))
            cardRect = self.stackView.GetRect()
            dist = 20 if event.AltDown() else (5 if event.ShiftDown() else 1)
            if code == wx.WXK_LEFT:
                if pos.x-dist < 0: dist = pos.x
                if dist > 0:
                    command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (-dist, 0))
                    commands.append(command)
            elif code == wx.WXK_RIGHT:
                if pos.x+dist > cardRect.Right-20: dist = cardRect.Right-20 - pos.x
                if dist > 0:
                    command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (dist, 0))
                    commands.append(command)
            elif code == wx.WXK_UP:
                if pos.y-dist < 0: dist = pos.y
                if dist > 0:
                    command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (0, -dist))
                    commands.append(command)
            elif code == wx.WXK_DOWN:
                if pos.y+dist > cardRect.Bottom-20: dist = cardRect.Bottom-20 - pos.y
                if dist > 0:
                    command = MoveUiViewCommand(True, 'Move', self.stackView, self.stackView.cardIndex, uiView.model, (0, dist))
                    commands.append(command)

        if len(commands):
            command = CommandGroup(True, "Move Views", commands)
            self.stackView.command_processor.Submit(command)

        if code == wx.WXK_TAB:
            allUiViews = self.stackView.GetAllUiViews()
            if len(allUiViews) > 0:
                if len(uiViews) > 0:
                    ui = uiViews[-1]
                    if ui == self.stackView.uiCard:
                        self.stackView.SelectUiView(allUiViews[0])
                    elif ui == allUiViews[-1]:
                        self.stackView.SelectUiView(self.stackView.uiCard)
                    else:
                        nextUi = allUiViews[allUiViews.index(ui) + 1]
                        self.stackView.SelectUiView(nextUi)
        event.Skip()


class ViewTool(BaseTool):
    def __init__(self, stackView, name):
        super().__init__(stackView)
        self.cursor = wx.CURSOR_CROSS
        self.name = name  # button, field, label, or image

    def OnMouseDown(self, uiView, event):
        self.targetUi = self.stackView.AddUiViewInternal(self.name)
        x, y = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        self.origMousePos = (x, y)
        self.targetUi.model.SetProperty("position", self.origMousePos)
        self.targetUi.model.SetProperty("size", [0,0])
        self.origSize = [0,0]
        self.targetUi.view.CaptureMouse()
        self.stackView.SelectUiView(self.targetUi)

    def OnMouseMove(self, uiView, event):
        if self.targetUi and self.targetUi.view.HasCapture():
            x, y = self.stackView.ScreenToClient(self.targetUi.view.ClientToScreen(event.GetPosition()))
            offset = (x-self.origMousePos[0], y-self.origMousePos[1])
            self.targetUi.model.SetProperty("size", [self.origSize[0]+offset[0], self.origSize[1]+offset[1]])
        event.Skip()

    def OnMouseUp(self, uiView, event):
        if self.targetUi and self.targetUi.view.HasCapture():
            self.targetUi.view.ReleaseMouse()
            endw, endh = self.targetUi.view.GetSize()
            offset = (endw-self.origSize[0], endh-self.origSize[1])
            if offset != (0, 0):
                model = self.targetUi.model
                command = AddNewUiViewCommand(True, 'Add View', self.stackView, self.stackView.cardIndex, model.type, model)
                self.stackView.RemoveUiViewByModel(model)
                self.stackView.command_processor.Submit(command)
                self.stackView.SelectUiView(self.stackView.GetUiViewByModel(model))
            self.stackView.SetFocus()
            self.targetUi = None


class PenTool(BaseTool):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.cursor = wx.CURSOR_PENCIL
        self.name = "pen"
        self.curLine = []
        self.pos = wx.Point(0,0)
        self.thickness = 0
        self.penColor = None
        self.targetUi = None

    def SetPenColor(self, color):
        self.penColor = color.GetAsString(flags=wx.C2S_HTML_SYNTAX)

    def SetFillColor(self, color):
        pass

    def SetThickness(self, num):
        self.thickness = num

    def OnMouseDown(self, uiView, event):
        self.pos = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))

        self.targetUi = self.stackView.AddUiViewInternal(self.name)
        self.targetUi.model.SetProperty("position", [0,0])
        self.targetUi.model.SetProperty("size", self.stackView.stackModel.GetProperty("size"))

        self.targetUi.view.CaptureMouse()
        self.curLine = []
        self.curLine.append(list(self.pos))
        self.targetUi.model.SetShape({"type": "pen", "penColor": self.penColor, "thickness": self.thickness, "points": self.curLine})

    def OnMouseMove(self, uiView, event):
        """
        Called when the mouse is in motion.  If the left button is
        dragging then draw a line from the last event position to the
        current one.  Save the coordinants for redraws.
        """
        if self.targetUi and self.targetUi.view.HasCapture():
            pos = event.GetPosition()
            coords = (pos.x, pos.y)
            if coords != (self.pos.x, self.pos.y):
                self.curLine.append(coords)
                self.targetUi.model.DidUpdateShape()
                self.pos = pos

    def OnMouseUp(self, uiView, event):
        """called when the left mouse button is released"""
        if self.targetUi and self.targetUi.view.HasCapture():
            model = self.targetUi.model
            self.curLine = []
            self.targetUi.view.ReleaseMouse()
            self.targetUi = None

            model.ReCropShape()

            command = AddNewUiViewCommand(True, 'Add Shape', self.stackView, self.stackView.cardIndex, model.type, model)
            self.stackView.RemoveUiViewByModel(model)
            self.stackView.command_processor.Submit(command)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(model))
        self.stackView.SetFocus()


class ShapeTool(BaseTool):
    def __init__(self, stackView, name):
        super().__init__(stackView)
        self.cursor = wx.CURSOR_CROSS
        self.name = name
        self.startPoint = None
        self.thickness = 0
        self.penColor = None
        self.fillColor = None
        self.targetUi = None

    def SetPenColor(self, color):
        self.penColor = color.GetAsString(flags=wx.C2S_HTML_SYNTAX)

    def SetFillColor(self, color):
        self.fillColor = color.GetAsString(flags=wx.C2S_HTML_SYNTAX)

    def SetThickness(self, num):
        self.thickness = num

    def OnMouseDown(self, uiView, event):
        self.startPoint = list(self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition())))

        self.targetUi = self.stackView.AddUiViewInternal(self.name)
        self.targetUi.model.SetProperty("position", [0,0])
        self.targetUi.model.SetProperty("size", self.stackView.stackModel.GetProperty("size"))

        self.targetUi.view.CaptureMouse()
        self.points = [self.startPoint, self.startPoint]
        self.targetUi.model.SetShape({"type": self.name, "penColor": self.penColor, "fillColor": self.fillColor,
                                      "thickness": self.thickness, "points": self.points})

    def OnMouseMove(self, uiView, event):
        """
        Called when the mouse is in motion.  If the left button is
        dragging then draw a line from the last event position to the
        current one.  Save the coordinants for redraws.
        """
        if self.targetUi and self.targetUi.view.HasCapture():
            pos = list(self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition())))
            if pos != self.points[1]:
                if event.ShiftDown():
                    dx = pos[0] - self.startPoint[0]
                    dy = pos[1] - self.startPoint[1]
                    if self.name == "line":
                        if abs(dx) > abs(dy):
                            self.points[1] = [pos[0], self.startPoint[1]]
                        else:
                            self.points[1] = [self.startPoint[0], pos[1]]
                    else:
                        if abs(dx) > abs(dy):
                            self.points[1] = [pos[0], self.startPoint[1] + (math.copysign(dx, dy))]
                        else:
                            self.points[1] = [self.startPoint[0] + (math.copysign(dy, dx)), pos[1]]
                else:
                    self.points[1] = pos
                self.targetUi.model.DidUpdateShape()

    def OnMouseUp(self, uiView, event):
        """called when the left mouse button is released"""
        if self.targetUi and self.targetUi.view.HasCapture():
            model = self.targetUi.model
            self.targetUi.view.ReleaseMouse()
            self.targetUi = None

            model.ReCropShape()

            command = AddNewUiViewCommand(True, 'Add Shape', self.stackView, self.stackView.cardIndex, model.type, model)
            self.stackView.RemoveUiViewByModel(model)
            self.stackView.command_processor.Submit(command)
            self.stackView.SelectUiView(self.stackView.GetUiViewByModel(model))
        self.stackView.SetFocus()
