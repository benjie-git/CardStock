import wx
from commands import *
from uiShape import ShapeModel
import math

"""
These are the tools that appear at the top of the Designer's ControlPanel.
The currently selected tool gets to handle mouse Down/Move/Up events, as well as key Down/Up events while editing the
stack in the Designer.  It also gets to Paint onto the stack window (used for showing the hand tool's selection
rectangle).  Each tool can also have a dedicated cursor, which overrides the cursors of the individual objects. 
"""


MOVE_THRESHOLD = 5


# quick function to return the manhattan distance between two points, as lists
def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class BaseTool(object):
    """
    Abstract Base for the real tool classes.
    """

    def __init__(self, stackManager):
        super().__init__()
        self.stackManager = stackManager
        self.targetUi = None
        self.cursor = None
        self.name = ""

    @classmethod
    def ToolFromName(cls, name, stackManager):
        if name == "hand":
            return HandTool(stackManager)
        elif name == "button" or name == "field" or name == "label" or name == "image":
            return ViewTool(stackManager, name)
        elif name == "pen":
            return PenTool(stackManager)
        elif name == "rect" or name == "roundrect" or name == "oval" or name == "line":
            return ShapeTool(stackManager, name)
        else:
            return HandTool(stackManager)

    def Activate(self):
        # Do anything you need to do when starting to use this tool
        pass

    def Deactivate(self):
        # Do anything you need to do when done with this tool
        pass

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

    def ConstrainDragPoint(self, objType, startPoint, event):
        pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        newPoint = pos
        if event.ShiftDown():
            dx = pos[0] - startPoint[0]
            dy = pos[1] - startPoint[1]
            if objType == "line":
                if abs(dx) > abs(dy) and abs(abs(dx) - abs(dy)) < abs(dx) / 3:
                    # Diagonal
                    newPoint = [startPoint[0] + dx, startPoint[1] + math.copysign(dx, dy)]
                elif abs(dx) < abs(dy) and abs(abs(dx) - abs(dy)) < abs(dy) / 3:
                    # Diagonal
                    newPoint = [startPoint[0] + math.copysign(dy, dx), startPoint[1] + dy]
                elif abs(dx) > abs(dy):
                    # Horizontal
                    newPoint = [pos[0], startPoint[1]]
                else:
                    # Vertical
                    newPoint = [startPoint[0], pos[1]]
            else:
                if abs(dx) > abs(dy):
                    # Square/Circle, as wide as the mouse drag
                    newPoint = [pos[0], startPoint[1] + (math.copysign(dx, dy))]
                else:
                    # Square/Circle, as tall as the mouse drag
                    newPoint = [startPoint[0] + (math.copysign(dy, dx)), pos[1]]
        return wx.Point(*newPoint)

    def ConstrainDragPointAspect(self, startPoint, startSize, event):
        pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        newPoint = pos
        if event.ShiftDown():
            dx = pos[0] - startPoint[0]
            dy = pos[1] - startPoint[1]
            scaleX = dx/startSize.width
            scaleY = dy/startSize.height
            scale = max(scaleX, scaleY)
            newSize = startSize * scale
            newPoint = [startPoint.x + newSize.width, startPoint.y + newSize.height]
        return wx.Point(*newPoint)


class HandTool(BaseTool):
    """
    The Hand tool allows selecting objects, moving and resizing them, and tabbing between them.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
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
        if uiView.parent == self.stackManager.uiCard or not uiView.parent:
            # Clicked on a top-level uiView or the card itself
            self.targetUi = uiView
        else:
            # Clicked on a group's subview
            oldSelection = self.stackManager.GetSelectedUiViews()
            self.targetUi = uiView
            while self.targetUi.parent and self.targetUi.parent.parent:
                if self.targetUi.parent.isSelected or (len(oldSelection) == 1 and \
                                                oldSelection[0].parent == self.targetUi.parent and \
                                                oldSelection[0] != self.targetUi):
                    # If the parent or a sibling of this subview was already selected
                    self.stackManager.SelectUiView(self.targetUi)
                    selectedGroupSubview = True
                    break
                self.targetUi = self.targetUi.parent
            while self.targetUi.parent and self.targetUi.parent.model.type == "group":
                self.targetUi = self.targetUi.parent

        self.absOrigin = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        self.relOrigin = self.absOrigin - wx.Point(self.targetUi.model.GetAbsolutePosition())
        self.stackManager.view.CaptureMouse()

        if self.targetUi.isSelected and self.shiftDown:
            self.deselectTarget = True

        if not selectedGroupSubview and not self.targetUi.isSelected:
            self.stackManager.SelectUiView(self.targetUi, self.shiftDown)

        self.oldFrames = {}
        selected = self.stackManager.GetSelectedUiViews()
        if self.targetUi not in selected:
            selected.append(self.targetUi)
        for ui in selected:
            frame = ui.model.GetFrame()
            self.oldFrames[ui.model.GetProperty("name")] = frame

    def OnMouseMove(self, uiView, event):
        if self.mode:
            pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            origSize = self.oldFrames[self.targetUi.model.GetProperty("name")].Size

            if self.mode == "click":
                if dist(list(pos), list(self.absOrigin)) > MOVE_THRESHOLD:
                    if self.targetUi.GetResizeBoxRect().Inflate(2).Contains(self.relOrigin):
                          self.StartResize()
                    else:
                        if self.targetUi.model.type == "card":
                            self.StartBoxSelect()
                        else:
                            self.StartMove()
                else:
                    return

            if self.mode == "box":
                self.stackManager.view.Refresh(True, self.selectionRect.Inflate(2))
                self.selectionRect = ShapeModel.RectFromPoints([self.absOrigin, pos])
                self.stackManager.view.Refresh(True, self.selectionRect.Inflate(2))
                self.UpdateBoxSelection()
                return

            if self.mode == "move":
                selectedViews = self.stackManager.GetSelectedUiViews()
                if len(selectedViews) == 1 and selectedViews[0].parent.model.type == "group":
                    selectedViews = [self.targetUi]
                for ui in selectedViews:
                    offset = (pos.x - self.absOrigin.x, pos.y - self.absOrigin.y)
                    origPos = self.oldFrames[ui.model.GetProperty("name")].Position
                    ui.model.SetProperty("position", [origPos.x + offset[0], origPos.y + offset[1]])
            elif self.mode == "resize":
                origPos = self.oldFrames[self.targetUi.model.GetProperty("name")].Position
                pos = self.ConstrainDragPointAspect(origPos, origSize, event)
                offset = (pos.x - self.absOrigin.x, pos.y - self.absOrigin.y)
                topLeft = (min(pos[0], origPos[0]), min(pos[1], origPos[1]))
                thickness = self.targetUi.model.GetProperty("penThickness")
                self.targetUi.model.SetProperty("position", topLeft)
                self.targetUi.model.SetProperty("size", [abs(origSize[0]+offset[0]), abs(origSize[1]+offset[1])])
                if self.targetUi.model.type in ['line', 'pen']:
                    (fx, fy) = ((pos[0] < origPos[0] + thickness/2), (pos[1] < origPos[1] + thickness/2))
                    self.targetUi.model.SetTempFlippedFlags(fx, fy)
        event.Skip()

    def StartBoxSelect(self):
        self.mode = "box"
        self.selectionRect = ShapeModel.RectFromPoints([self.absOrigin])
        self.stackManager.view.Refresh(True, self.selectionRect.Inflate(2))

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
        if self.stackManager.view.HasCapture():
            self.stackManager.view.ReleaseMouse()

        if self.mode == "click":
            if self.deselectTarget and self.targetUi.isSelected:
                self.stackManager.SelectUiView(self.targetUi, True)
            elif not event.ShiftDown():
                topView = self.stackManager.HitTest(self.absOrigin, False)
                if topView and topView.model.parent.type != "group":
                    self.stackManager.SelectUiView(topView)
        elif self.mode == "box":
            self.stackManager.view.Refresh(True, self.selectionRect.Inflate(2))
            self.selectionRect = None
        elif self.mode == "move":
            pos = self.targetUi.model.GetAbsolutePosition()
            viewOrigin = self.oldFrames[self.targetUi.model.GetProperty("name")].Position
            offset = (pos[0] - viewOrigin.x, pos[1] - viewOrigin.y)
            if offset != (0, 0):
                selectedViews = self.stackManager.GetSelectedUiViews()
                if len(selectedViews) == 1 and selectedViews[0].parent.model.type == "group":
                    selectedViews = [self.targetUi]
                models = [ui.model for ui in selectedViews]
                command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex,
                                             models, offset)
                for m in models:
                    viewOrigin = self.oldFrames[m.GetProperty("name")].Position
                    m.SetProperty("position", viewOrigin)
                self.stackManager.command_processor.Submit(command)
        elif self.mode == "resize":
            pos = self.targetUi.model.GetAbsolutePosition()
            viewOrigin = self.oldFrames[self.targetUi.model.GetProperty("name")].Position
            moveOffset = (pos[0] - viewOrigin.x, pos[1] - viewOrigin.y)

            endw, endh = self.targetUi.model.GetProperty("size")
            origSize = self.oldFrames[self.targetUi.model.GetProperty("name")].Size
            sizeOffset = (endw-origSize[0], endh-origSize[1])

            if moveOffset != (0, 0) or sizeOffset != (0, 0):
                moveCommand = MoveUiViewsCommand(True, 'Resize-Move', self.stackManager, self.stackManager.cardIndex,
                                                 [self.targetUi.model], moveOffset)
                sizeCommand = ResizeUiViewCommand(True, 'Resize-Resize', self.stackManager, self.stackManager.cardIndex,
                                                  self.targetUi.model, sizeOffset)
                commands = [moveCommand, sizeCommand]
                if self.targetUi.model.type in ['line', 'pen']:
                    (fx, fy) = (self.targetUi.model.xFlipped, self.targetUi.model.yFlipped)
                    flipCommand = FlipShapeCommand(True, 'Resize-Flip', self.stackManager, self.stackManager.cardIndex,
                                                   self.targetUi.model, fx, fy)
                    commands.append(flipCommand)
                self.targetUi.model.SetProperty("position", viewOrigin)
                self.targetUi.model.SetProperty("size", origSize)
                command = CommandGroup(True, "Resize", commands)
                self.stackManager.command_processor.Submit(command)

        self.mode = None
        self.stackManager.view.SetFocus()
        self.targetUi = None
        event.Skip()

    def UpdateBoxSelection(self):
        self.stackManager.SelectUiView(None)
        for ui in self.stackManager.uiViews:
            select = self.selectionRect.Contains(ui.model.GetCenter())
            if select:
                self.stackManager.SelectUiView(ui, True)

    def OnKeyDown(self, uiViewIn, event):
        if event.RawControlDown() or event.CmdDown():
            event.Skip()
            return

        uiViews = []
        if uiViewIn and uiViewIn.model.type == "card":
            uiViews = self.stackManager.GetSelectedUiViews()

        code = event.GetKeyCode()

        if code == wx.WXK_TAB:
            allUiViews = self.stackManager.GetAllUiViews()
            searchReverse = event.ShiftDown()
            if len(uiViews) == 0:
                nextUi = self.stackManager.uiCard
                self.stackManager.SelectUiView(nextUi)
            else:
                ui = uiViews[-1]
                if len(allUiViews) > 0:
                    if not searchReverse:
                        if ui == self.stackManager.uiCard:
                            self.stackManager.SelectUiView(allUiViews[0])
                        elif ui == allUiViews[-1]:
                            self.stackManager.SelectUiView(self.stackManager.uiCard)
                        else:
                            nextUi = allUiViews[allUiViews.index(ui) + 1]
                            self.stackManager.SelectUiView(nextUi)
                    else:
                        if ui == self.stackManager.uiCard:
                            self.stackManager.SelectUiView(allUiViews[-1])
                        elif ui == allUiViews[0]:
                            self.stackManager.SelectUiView(self.stackManager.uiCard)
                        else:
                            nextUi = allUiViews[allUiViews.index(ui) - 1]
                            self.stackManager.SelectUiView(nextUi)

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
            cardRect = self.stackManager.view.GetRect()
            dist = 20 if event.AltDown() else (5 if event.ShiftDown() else 1)
            if code == wx.WXK_LEFT:
                if pos.x-dist < 0: dist = pos.x
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (-dist, 0))
            elif code == wx.WXK_RIGHT:
                if pos.x+dist > cardRect.Right-20: dist = cardRect.Right-20 - pos.x
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (dist, 0))
            elif code == wx.WXK_UP:
                if pos.y-dist < 0: dist = pos.y
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (0, -dist))
            elif code == wx.WXK_DOWN:
                if pos.y+dist > cardRect.Bottom-20: dist = cardRect.Bottom-20 - pos.y
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (0, dist))

            if command:
                self.stackManager.command_processor.Submit(command)

        event.Skip()


class ViewTool(BaseTool):
    """
    The View tool allows creating Buttons, Text Fields, Text Labels, and Images.
    """

    def __init__(self, stackManager, name):
        super().__init__(stackManager)
        self.cursor = wx.CURSOR_CROSS
        self.name = name  # button, field, label, or image

    def OnMouseDown(self, uiView, event):
        self.targetUi = None
        x, y = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        self.origMousePos = (x, y)
        self.stackManager.view.CaptureMouse()

    def OnMouseMove(self, uiView, event):
        if self.stackManager.view.HasCapture():
            pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            pos = self.ConstrainDragPoint(self.name, self.origMousePos, event)

            if not self.targetUi and dist(self.origMousePos, pos) > MOVE_THRESHOLD:
                self.targetUi = self.stackManager.AddUiViewInternal(self.name)
                self.targetUi.model.SetProperty("position", self.origMousePos)
                self.targetUi.model.SetProperty("size", [0,0])
                self.stackManager.SelectUiView(self.targetUi)
                self.origSize = [0,0]

            if self.targetUi:
                offset = (pos.x-self.origMousePos[0], pos.y-self.origMousePos[1])
                topLeft = (min(pos[0], self.origMousePos[0]), min(pos[1], self.origMousePos[1]))
                self.targetUi.model.SetProperty("position", topLeft)
                self.targetUi.model.SetProperty("size", [abs(self.origSize[0]+offset[0]), abs(self.origSize[1]+offset[1])])
        event.Skip()

    def OnMouseUp(self, uiView, event):
        if self.stackManager.view.HasCapture():
            self.stackManager.view.ReleaseMouse()
            if self.targetUi:
                endw, endh = self.targetUi.model.GetProperty("size")
                offset = (endw-self.origSize[0], endh-self.origSize[1])
                if offset != (0, 0):
                    model = self.targetUi.model
                    command = AddNewUiViewCommand(True, 'Add View', self.stackManager, self.stackManager.cardIndex, model.type, model)
                    self.stackManager.RemoveUiViewByModel(model)
                    self.stackManager.command_processor.Submit(command)
                    self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
                self.stackManager.view.SetFocus()
                self.targetUi = None

    def Paint(self, gc):
        if self.targetUi and self.stackManager.view.HasCapture():
            gc.SetPen(wx.Pen('Blue', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.targetUi.model.GetAbsoluteFrame())

class PenTool(BaseTool):
    """
    The View tool allows creating shape objects that are drawn freehand.
    """

    SMOOTHING_DIST = 8

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.cursor = wx.CURSOR_PENCIL
        self.name = "pen"
        self.curLine = []
        self.pos = wx.Point(0,0)
        self.thickness = 0
        self.penColor = None
        self.targetUi = None

    def SetPenColor(self, color):
        self.penColor = color

    def SetFillColor(self, color):
        pass

    def SetThickness(self, num):
        self.thickness = num

    def OnMouseDown(self, uiView, event):
        self.pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))

        self.targetUi = self.stackManager.AddUiViewInternal(self.name)
        self.targetUi.model.SetProperty("position", [0,0])
        self.targetUi.model.SetProperty("size", self.stackManager.stackModel.GetProperty("size"))
        # self.stackManager.SelectUiView(self.targetUi)

        self.stackManager.view.CaptureMouse()
        self.curLine = []
        self.curLine.append(list(self.pos))
        self.targetUi.model.SetShape({"type": "pen", "penColor": self.penColor, "thickness": self.thickness, "points": self.curLine})

    def OnMouseMove(self, uiView, event):
        if self.targetUi and self.stackManager.view.HasCapture():
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
        if self.targetUi and self.stackManager.view.HasCapture():
            model = self.targetUi.model
            self.curLine = []
            self.stackManager.view.ReleaseMouse()
            self.targetUi = None

            model.ReCropShape()

            command = AddNewUiViewCommand(True, 'Add Shape', self.stackManager, self.stackManager.cardIndex, model.type, model)
            self.stackManager.RemoveUiViewByModel(model)
            self.stackManager.command_processor.Submit(command)
            self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
        self.stackManager.view.SetFocus()


class ShapeTool(BaseTool):
    """
    The Shape tool allows drawing lines, ovals, rectangles, and round rectangles.
    """

    def __init__(self, stackManager, name):
        super().__init__(stackManager)
        self.cursor = wx.CURSOR_CROSS
        self.name = name
        self.startPoint = None
        self.thickness = 0
        self.penColor = None
        self.fillColor = None
        self.targetUi = None

    def SetPenColor(self, color):
        self.penColor = color

    def SetFillColor(self, color):
        self.fillColor = color

    def SetThickness(self, num):
        self.thickness = num

    def OnMouseDown(self, uiView, event):
        self.startPoint = list(self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition())))
        self.targetUi = None
        self.stackManager.view.CaptureMouse()
        self.points = [self.startPoint, self.startPoint]

    def OnMouseMove(self, uiView, event):
        if self.stackManager.view.HasCapture():
            pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            if not self.targetUi and dist(self.startPoint, pos) > MOVE_THRESHOLD:
                self.targetUi = self.stackManager.AddUiViewInternal(self.name)
                self.targetUi.model.SetProperty("position", [0, 0])
                self.targetUi.model.SetProperty("size", self.stackManager.stackModel.GetProperty("size"))
                self.targetUi.model.SetShape({"type": self.name, "penColor": self.penColor, "fillColor": self.fillColor,
                                              "thickness": self.thickness, "points": self.points})
                # self.stackManager.SelectUiView(self.targetUi)
            if self.targetUi:
                if pos != self.points[1]:
                    self.points[1] = self.ConstrainDragPoint(self.name, self.startPoint, event)
                    self.targetUi.model.DidUpdateShape()

    def OnMouseUp(self, uiView, event):
        if self.stackManager.view.HasCapture():
            self.stackManager.view.ReleaseMouse()
            if self.targetUi:
                model = self.targetUi.model
                self.targetUi = None

                model.ReCropShape()

                command = AddNewUiViewCommand(True, 'Add Shape', self.stackManager, self.stackManager.cardIndex, model.type, model)
                self.stackManager.RemoveUiViewByModel(model)
                self.stackManager.command_processor.Submit(command)
                self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
                # self.stackManager.view.Refresh(True)
        self.stackManager.view.SetFocus()

    # def Paint(self, gc):
    #     if self.targetUi and self.stackManager.view.HasCapture():
    #         gc.SetPen(wx.Pen('Blue', 1, wx.PENSTYLE_DOT))
    #         gc.SetBrush(wx.TRANSPARENT_BRUSH)
    #         f = self.targetUi.model.RectFromPoints(self.targetUi.model.GetScaledPoints())
    #         f.Offset(wx.Point(self.targetUi.model.GetAbsolutePosition()))
    #         f.Inflate(self.targetUi.model.GetProperty("penThickness"))
    #         gc.DrawRectangle(f)
