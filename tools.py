import wx
from commands import *
from uiShape import ShapeModel
import math


MOVE_THRESHOLD = 5
MAC_BUTTON_OFFSET_HACK = wx.Point(6,4)


# quick function to return the manhattan distance between two points, as lists
def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


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

    def Paint(self, gc):
        pass


class HandTool(BaseTool):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.cursor = None
        self.name = "hand"
        self.selectionRect = None
        self.mode = None  # click, box, move, resize
        self.shiftDown = False

    def OnMouseDown(self, uiView, event):
        self.mode = "click"
        self.shiftDown = event.ShiftDown()
        selectedGroupSubview = False
        self.deselectTarget = False
        if uiView.parent == self.stackView.uiCard or not uiView.parent:
            # Clicked on a top-level uiView or the card itself
            self.targetUi = uiView
        else:
            # Clicked on a group's subview
            oldSelection = self.stackView.GetSelectedUiViews()
            self.targetUi = uiView
            while self.targetUi.parent and self.targetUi.parent.parent:
                if self.targetUi.parent.isSelected or (len(oldSelection) == 1 and \
                                                oldSelection[0].parent == self.targetUi.parent and \
                                                oldSelection[0] != self.targetUi):
                    # If the parent or a sibling of this subview was already selected
                    self.stackView.SelectUiView(self.targetUi)
                    selectedGroupSubview = True
                    break
                self.targetUi = self.targetUi.parent
            while self.targetUi.parent and self.targetUi.parent.model.type == "group":
                self.targetUi = self.targetUi.parent

        self.absOrigin = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        self.relOrigin = self.absOrigin - wx.Point(self.targetUi.model.GetAbsolutePosition())
        self.stackView.CaptureMouse()

        if self.targetUi.isSelected and self.shiftDown:
            self.deselectTarget = True

        if not selectedGroupSubview and not self.targetUi.isSelected:
            self.stackView.SelectUiView(self.targetUi, self.shiftDown)

        self.oldFrames = {}
        selected = self.stackView.GetSelectedUiViews()
        if self.targetUi not in selected:
            selected.append(self.targetUi)
        for ui in selected:
            frame = ui.model.GetFrame()
            self.oldFrames[ui.model.GetProperty("name")] = frame

    def OnMouseMove(self, uiView, event):
        if self.mode:
            pos = event.GetPosition()
            origSize = self.oldFrames[self.targetUi.model.GetProperty("name")].Size
            if wx.Platform == '__WXMAC__' and self.targetUi.model.type == "button" and self.targetUi.model.GetProperty("border"):
                # Button views are bigger than specified???
                pos.x += MAC_BUTTON_OFFSET_HACK.x
                pos.y += MAC_BUTTON_OFFSET_HACK.y

            if self.mode == "click":
                if dist(list(pos), list(self.absOrigin)) > MOVE_THRESHOLD:
                    if self.targetUi.GetResizeBoxRect().Inflate(4).Contains(self.relOrigin):
                          self.StartResize()
                    else:
                        if self.targetUi.model.type == "card":
                            self.StartBoxSelect()
                        else:
                            self.StartMove()
                else:
                    return

            if self.mode == "box":
                self.stackView.Refresh(True, self.selectionRect.Inflate(2))
                self.selectionRect = ShapeModel.RectFromPoints([self.absOrigin, pos])
                self.stackView.Refresh(True, self.selectionRect.Inflate(2))
                self.UpdateSelection()
                return

            offset = (pos.x - self.absOrigin.x, pos.y - self.absOrigin.y)
            if self.mode == "move":
                selectedViews = self.stackView.GetSelectedUiViews()
                if len(selectedViews) == 1 and selectedViews[0].parent.model.type == "group":
                    selectedViews = [self.targetUi]
                for ui in selectedViews:
                    origPos = self.oldFrames[ui.model.GetProperty("name")].Position
                    ui.model.SetProperty("position", [origPos.x + offset[0], origPos.y + offset[1]])
            elif self.mode == "resize":
                self.targetUi.model.SetProperty("size", [origSize.Width + offset[0], origSize.Height + offset[1]])
        event.Skip()

    def StartBoxSelect(self):
        self.mode = "box"
        self.selectionRect = ShapeModel.RectFromPoints([self.absOrigin])
        self.stackView.Refresh(True, self.selectionRect.Inflate(2))

    def Paint(self, gc):
        if self.selectionRect:
            gc.SetPen(wx.Pen('Blue', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.selectionRect)

    def StartMove(self):
        self.mode = "move"

    def StartResize(self):
        self.mode = "resize"

    def OnMouseUp(self, uiView, event):
        if self.stackView.HasCapture():
            self.stackView.ReleaseMouse()

        if self.mode == "click":
            if self.deselectTarget and self.targetUi.isSelected:
                self.stackView.SelectUiView(self.targetUi, True)
        elif self.mode == "box":
            self.stackView.Refresh(True, self.selectionRect.Inflate(2))
            self.selectionRect = None
        elif self.mode == "move":
            pos = self.targetUi.model.GetAbsolutePosition()
            viewOrigin = self.oldFrames[self.targetUi.model.GetProperty("name")].Position
            offset = (pos[0] - viewOrigin.x, pos[1] - viewOrigin.y)
            if offset != (0, 0):
                selectedViews = self.stackView.GetSelectedUiViews()
                if len(selectedViews) == 1 and selectedViews[0].parent.model.type == "group":
                    selectedViews = [self.targetUi]
                models = [ui.model for ui in selectedViews]
                command = MoveUiViewsCommand(True, 'Move', self.stackView, self.stackView.cardIndex,
                                             models, offset)
                for m in models:
                    viewOrigin = self.oldFrames[m.GetProperty("name")].Position
                    m.SetProperty("position", viewOrigin)
                self.stackView.command_processor.Submit(command)
        elif self.mode == "resize":
            endw, endh = self.targetUi.model.GetProperty("size")
            origSize = self.oldFrames[self.targetUi.model.GetProperty("name")].Size
            offset = (endw-origSize[0], endh-origSize[1])
            if offset != (0, 0):
                command = ResizeUiViewCommand(True, 'Resize', self.stackView, self.stackView.cardIndex, self.targetUi.model, offset)
                self.targetUi.model.SetProperty("size", origSize)
                self.stackView.command_processor.Submit(command)

        self.mode = None
        self.stackView.SetFocus()
        self.targetUi = None
        event.Skip()

    def UpdateSelection(self):
        self.stackView.SelectUiView(None)
        for ui in self.stackView.uiViews:
            select = self.selectionRect.Contains(ui.model.GetCenter())
            if select:
                self.stackView.SelectUiView(ui, True)

    def OnKeyDown(self, uiViewIn, event):
        if event.RawControlDown() or event.CmdDown():
            event.Skip()
            return

        uiViews = []
        if uiViewIn and uiViewIn.model.type == "card":
            uiViews = self.stackView.GetSelectedUiViews()

        code = event.GetKeyCode()

        if code == wx.WXK_TAB:
            allUiViews = self.stackView.GetAllUiViews()
            searchReverse = event.ShiftDown()
            if len(uiViews) == 0:
                nextUi = self.stackView.uiCard
                self.stackView.SelectUiView(nextUi)
            else:
                ui = uiViews[-1]
                if len(allUiViews) > 0:
                    if not searchReverse:
                        if ui == self.stackView.uiCard:
                            self.stackView.SelectUiView(allUiViews[0])
                        elif ui == allUiViews[-1]:
                            self.stackView.SelectUiView(self.stackView.uiCard)
                        else:
                            nextUi = allUiViews[allUiViews.index(ui) + 1]
                            self.stackView.SelectUiView(nextUi)
                    else:
                        if ui == self.stackView.uiCard:
                            self.stackView.SelectUiView(allUiViews[-1])
                        elif ui == allUiViews[0]:
                            self.stackView.SelectUiView(self.stackView.uiCard)
                        else:
                            nextUi = allUiViews[allUiViews.index(ui) - 1]
                            self.stackView.SelectUiView(nextUi)

        for uiView in uiViews.copy():
            if uiView.model.type == "card":
                uiViews.remove(uiView)
            if uiView.parent and uiView.parent.model.type == "group":
                uiViews.remove(uiView)

        if len(uiViews):
            sharedFrame = uiViews[0].model.GetFrame()
            for v in uiViews[1:]:
                sharedFrame = sharedFrame.Union(v.model.GetFrame())

            models = [v.model for v in uiViews]
            command = None
            pos = sharedFrame.TopLeft
            cardRect = self.stackView.GetRect()
            dist = 20 if event.AltDown() else (5 if event.ShiftDown() else 1)
            if code == wx.WXK_LEFT:
                if pos.x-dist < 0: dist = pos.x
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackView, self.stackView.cardIndex, models, (-dist, 0))
            elif code == wx.WXK_RIGHT:
                if pos.x+dist > cardRect.Right-20: dist = cardRect.Right-20 - pos.x
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackView, self.stackView.cardIndex, models, (dist, 0))
            elif code == wx.WXK_UP:
                if pos.y-dist < 0: dist = pos.y
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackView, self.stackView.cardIndex, models, (0, -dist))
            elif code == wx.WXK_DOWN:
                if pos.y+dist > cardRect.Bottom-20: dist = cardRect.Bottom-20 - pos.y
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackView, self.stackView.cardIndex, models, (0, dist))

            if command:
                self.stackView.command_processor.Submit(command)

        event.Skip()


class ViewTool(BaseTool):
    def __init__(self, stackView, name):
        super().__init__(stackView)
        self.cursor = wx.CURSOR_CROSS
        self.name = name  # button, field, label, or image

    def OnMouseDown(self, uiView, event):
        self.targetUi = None
        x, y = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        self.origMousePos = (x, y)
        self.stackView.CaptureMouse()

    def OnMouseMove(self, uiView, event):
        if self.stackView.HasCapture():
            pos = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            if not self.targetUi and dist(self.origMousePos, pos) > MOVE_THRESHOLD:
                self.targetUi = self.stackView.AddUiViewInternal(self.name)
                self.targetUi.model.SetProperty("position", self.origMousePos)
                self.targetUi.model.SetProperty("size", [0,0])
                self.origSize = [0,0]
                self.stackView.SelectUiView(self.targetUi)

            if self.targetUi:
                offset = (pos.x-self.origMousePos[0], pos.y-self.origMousePos[1])
                self.targetUi.model.SetProperty("size", [self.origSize[0]+offset[0], self.origSize[1]+offset[1]])
        event.Skip()

    def OnMouseUp(self, uiView, event):
        if self.stackView.HasCapture():
            self.stackView.ReleaseMouse()
            if self.targetUi:
                endw, endh = self.targetUi.model.GetProperty("size")
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
    SMOOTHING_DIST = 8

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

        self.stackView.CaptureMouse()
        self.curLine = []
        self.curLine.append(list(self.pos))
        self.targetUi.model.SetShape({"type": "pen", "penColor": self.penColor, "thickness": self.thickness, "points": self.curLine})

    def OnMouseMove(self, uiView, event):
        if self.targetUi and self.stackView.HasCapture():
            pos = event.GetPosition()
            coords = (pos.x, pos.y)
            if coords != (self.pos.x, self.pos.y):
                if len(self.curLine) >= 2 and dist(coords, self.curLine[-2]) < self.SMOOTHING_DIST:
                    self.curLine[-1] = coords
                else:
                    self.curLine.append(coords)
                self.targetUi.model.DidUpdateShape()
                self.pos = pos

    def OnMouseUp(self, uiView, event):
        if self.targetUi and self.stackView.HasCapture():
            model = self.targetUi.model
            self.curLine = []
            self.stackView.ReleaseMouse()
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
        self.targetUi = None
        self.stackView.CaptureMouse()
        self.points = [self.startPoint, self.startPoint]

    def OnMouseMove(self, uiView, event):
        if self.stackView.HasCapture():
            pos = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            if not self.targetUi and dist(self.startPoint, pos) > MOVE_THRESHOLD:
                self.targetUi = self.stackView.AddUiViewInternal(self.name)
                self.targetUi.model.SetProperty("position", [0, 0])
                self.targetUi.model.SetProperty("size", self.stackView.stackModel.GetProperty("size"))
                self.targetUi.model.SetShape({"type": self.name, "penColor": self.penColor, "fillColor": self.fillColor,
                                              "thickness": self.thickness, "points": self.points})
            if self.targetUi:
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
        if self.stackView.HasCapture():
            self.stackView.ReleaseMouse()
            if self.targetUi:
                model = self.targetUi.model
                self.targetUi = None

                model.ReCropShape()

                command = AddNewUiViewCommand(True, 'Add Shape', self.stackView, self.stackView.cardIndex, model.type, model)
                self.stackView.RemoveUiViewByModel(model)
                self.stackView.command_processor.Submit(command)
                self.stackView.SelectUiView(self.stackView.GetUiViewByModel(model))
        self.stackView.SetFocus()


class SelectionBox(wx.Window):
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.startPoint = wx.Point(0,0)
        self.endPoint = wx.Point(0,0)

    def UpdateFrame(self):
        rect = wx.Rect(self.startPoint, (1,1))
        rect = rect.Union(wx.Rect(self.endPoint, (1,1)))
        rect = wx.Rect(rect.Left-1, rect.Top-1, rect.Width, rect.Height)
        self.SetRect(rect)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('Blue', 1, wx.PENSTYLE_SHORT_DASH))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle((1, 1), (self.GetSize()[0]-1, self.GetSize()[1]-1))
