# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx

import generator
from appCommands import *
from uiShape import UiShape, ShapeModel
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
        elif name in ["button", "field", "label", "image", "webview"]:
            return ViewTool(stackManager, name)
        elif name == "pen":
            return PenTool(stackManager)
        elif name == "polygon":
            return PolygonTool(stackManager)
        elif name in ["rect", "roundrect", "oval", "line"]:
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
        pass

    def OnKeyUp(self, uiView, event):
        pass

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
            elif objType == "drag":
                if abs(dx) > abs(dy):
                    # Square/Circle, as wide as the mouse drag
                    newPoint = [pos[0], startPoint[1]]
                else:
                    # Square/Circle, as tall as the mouse drag
                    newPoint = [startPoint[0], pos[1]]
            else:
                if abs(dx) > abs(dy):
                    # Square/Circle, as wide as the mouse drag
                    newPoint = [pos[0], startPoint[1] + (math.copysign(dx, dy))]
                else:
                    # Square/Circle, as tall as the mouse drag
                    newPoint = [startPoint[0] + (math.copysign(dy, dx)), pos[1]]
        return wx.Point(*(int(x) for x in newPoint))


class HandTool(BaseTool):
    """
    The Hand tool allows selecting objects, moving and resizing them, and tabbing between them.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.cursor = None
        self.name = "hand"
        self.selectionRect = None
        self.lastBoxList = None
        self.mode = None  # click, box, move, resize
        self.shiftDown = False
        self.xFlipped = False
        self.yFlipped = False
        self.resizeCorner = None
        self.resizeAnchorPointLocal = None
        self.resizeAnchorPointAbs = None
        self.resizeCardLastSize = None
        self.resizeAff = None
        self.resizeAffInverted = None
        self.origRotation = None

    def Activate(self):
        if len(self.stackManager.GetSelectedUiViews()) == 0:
            self.stackManager.SelectUiView(self.stackManager.uiCard)

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
        self.relOrigin = self.absOrigin - wx.Point(tuple(int(x) for x in self.targetUi.model.GetAbsolutePosition()))
        self.stackManager.view.CaptureMouse()

        if self.targetUi.isSelected and self.shiftDown:
            self.deselectTarget = True

        if not selectedGroupSubview and not self.targetUi.isSelected:
            if self.targetUi.model.type == "card" and (self.absOrigin.y < 0 or self.absOrigin.x > self.targetUi.model.GetProperty("size").width):
                # Don't select card when a click starts outside of the card.
                pass
            else:
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
                    # If we've dragged a few pixels since mouse-down, start a dragging action
                    # This can be dragging a selection box, moving an object, resizing, or rotating,
                    # depending on where the click started.
                    objRect = self.targetUi.model.GetAbsoluteFrame()
                    for k,r in self.targetUi.GetResizeBoxRects().items():
                        if r.Inflate(2).Contains(self.absOrigin):
                            # Drag started in a resize box
                            self.resizeCorner = ("L" in k, "B" in k)
                            self.resizeAnchorPointLocal = wx.Point(0 if "R" in k else origSize.width,
                                                                   0 if "T" in k else origSize.height)
                            self.resizeCardLastSize = objRect.Size
                            self.resizeAff = self.targetUi.model.GetAffineTransform()
                            self.resizeAffInverted = wx.AffineMatrix2D(self.resizeAff)
                            self.resizeAnchorPointAbs = self.resizeAff.TransformPoint(*self.resizeAnchorPointLocal)
                            self.resizeAff.Invert()
                            self.StartResize()
                            return
                    rotPt = self.targetUi.GetRotationHandlePoint()
                    if rotPt:
                        rotPt = tuple(int(x) for x in rotPt)
                        r = wx.Rect(wx.Point(rotPt)-(6,6), (12,12))
                        if r.Contains(self.absOrigin):
                            # Drag started in a rotate knob
                            self.origRotation = self.targetUi.model.GetProperty("rotation")
                            self.StartRotate()
                            return
                    if self.resizeCorner is None:
                        if self.targetUi.model.type == "card":
                            # Drag started on the card
                            self.StartBoxSelect()
                        else:
                            # Drag started on any other object
                            self.StartMove()
                else:
                    return

            if self.mode == "box":
                # We're already dragging out a selection box
                self.selectionRect = ShapeModel.RectFromPoints([self.absOrigin, pos])
                self.stackManager.view.Refresh()
                self.UpdateBoxSelection()
                return

            if self.mode == "move":
                # We're dragging/moving an object
                selectedViews = self.stackManager.GetSelectedUiViews()
                if len(selectedViews) == 1 and selectedViews[0].parent and selectedViews[0].parent.model.type == "group":
                    selectedViews = [self.targetUi]
                pos = self.ConstrainDragPoint("drag", self.absOrigin, event)
                for ui in selectedViews:
                    offset = (pos.x - self.absOrigin.x, pos.y - self.absOrigin.y)
                    origPos = self.oldFrames[ui.model.GetProperty("name")].Position
                    ui.model.SetProperty("position", [origPos.x + offset[0], origPos.y + offset[1]])

            elif self.mode == "rotate":
                # We're rotating an object
                center = self.targetUi.model.GetCenter()
                vector = pos - tuple((int(x) for x in center))
                if vector.y == 0:
                    rot = 90 if vector.x > 0 else -90
                else:
                    rot = round(math.degrees(math.atan2(vector.x, vector.y)), 1)
                if event.ShiftDown():
                    rot = int(((rot+2)%360) / 5) * 5
                if event.AltDown():
                    rot = int(((rot+22)%360) / 45) * 45
                self.targetUi.model.SetProperty("rotation", rot)

            elif self.mode == "resize":
                # We're resizing an object
                if self.targetUi.model.type == "card":
                    pos = self.ConstrainDragPointAspect(self.resizeAnchorPointLocal, origSize, pos, event.ShiftDown())
                    newSize = (pos[0], self.resizeCardLastSize[1] - pos[1])
                    self.targetUi.model.SetProperty("size", newSize)
                    self.resizeAnchorPointLocal = wx.Point(0, newSize[1])
                    self.resizeCardLastSize = newSize
                else:
                    localPos = self.resizeAff.TransformPoint(*pos)
                    localPos = self.ConstrainDragPointAspect(self.resizeAnchorPointLocal, origSize, localPos, event.ShiftDown())
                    pos = self.resizeAffInverted.TransformPoint(*localPos)
                    newRect = wx.Rect(wx.Point(int(min(self.resizeAnchorPointLocal[0], localPos[0])),
                                               int(min(self.resizeAnchorPointLocal[1], localPos[1]))),
                                      wx.Point(int(max(self.resizeAnchorPointLocal[0], localPos[0])),
                                               int(max(self.resizeAnchorPointLocal[1], localPos[1]))))

                    thickness = 0
                    if isinstance(self.targetUi, UiShape):
                        # Account for thickness of shapes while resizing
                        thickness = self.targetUi.model.GetProperty("pen_thickness")
                        if localPos[0] == newRect.Left:
                            newRect.Left += int(min(thickness/2, newRect.Width))
                            newRect.Width -= int(min(thickness/2, newRect.Width))
                        else:
                            newRect.Right -= int(thickness / 2)
                        if localPos[1] == newRect.Top:
                            newRect.Top += int(min(thickness/2, newRect.Height))
                            newRect.Height -= int(min(thickness/2, newRect.Height))
                        else:
                            newRect.Bottom -= int(thickness / 2)

                    if self.resizeCorner[0]:
                        xFlipped = (localPos[0] > self.resizeAnchorPointLocal[0] + thickness / 2)
                    else:
                        xFlipped = (localPos[0] < self.resizeAnchorPointLocal[0] + thickness / 2)

                    if self.resizeCorner[1]:
                        yFlipped = (localPos[1] > self.resizeAnchorPointLocal[1] + thickness / 2)
                    else:
                        yFlipped = (localPos[1] < self.resizeAnchorPointLocal[1] + thickness / 2)

                    flipX = (xFlipped != self.xFlipped)
                    flipY = (yFlipped != self.yFlipped)
                    self.xFlipped = xFlipped
                    self.yFlipped = yFlipped
                    self.targetUi.model.PerformFlips(flipX, flipY)

                    unrotRect = self.targetUi.model.UnrotatedRectFromAbsPoints(wx.Point(self.resizeAnchorPointAbs),
                                                                               wx.Point(int(pos[0]), int(pos[1])))
                    self.targetUi.model.SetProperty("position", unrotRect.TopLeft, notify=False)
                    self.targetUi.model.SetProperty("size", unrotRect.Size)

        event.Skip()

    def ConstrainDragPointAspect(self, startPoint, startSize, pos, shiftDown):
        if shiftDown:
            dx = pos[0] - startPoint[0]
            dy = pos[1] - startPoint[1]
            scaleX = abs(dx/startSize.width)
            scaleY = abs(dy/startSize.height)
            scale = max(scaleX, scaleY)
            newSize = startSize * scale
            if dx > 0:
                newX = startPoint.x + newSize.width
            else:
                newX = startPoint.x - newSize.width
            if dy > 0:
                newY = startPoint.y + newSize.height
            else:
                newY = startPoint.y - newSize.height
            return wx.Point(int(newX), int(newY))
        else:
            return pos

    def StartBoxSelect(self):
        self.mode = "box"
        self.selectionRect = ShapeModel.RectFromPoints([self.absOrigin])
        self.lastBoxList = []

    def Paint(self, gc):
        if self.selectionRect:
            gc.SetPen(wx.Pen('Blue', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.selectionRect)

    def StartMove(self):
        self.mode = "move"

    def StartResize(self):
        self.mode = "resize"
        self.xFlipped = False
        self.yFlipped = False
        self.stackManager.SelectUiView(self.targetUi)

    def StartRotate(self):
        self.mode = "rotate"
        self.stackManager.SelectUiView(self.targetUi)

    def OnMouseUp(self, uiView, event):
        if self.stackManager.view.HasCapture():
            self.stackManager.view.ReleaseMouse()

        if self.mode == "click":
            if self.deselectTarget and self.targetUi.isSelected:
                self.stackManager.SelectUiView(self.targetUi, True)
            elif not event.ShiftDown():
                topView = self.stackManager.HitTest(self.absOrigin, False)
                if topView:
                    if not topView.model.IsAncestorOf(self.targetUi.model):
                        ui = topView
                        while ui.model.parent.type not in ("card", "stack"):
                            ui = ui.parent
                        self.stackManager.SelectUiView(ui)
        elif self.mode == "box":
            self.selectionRect = None
            self.lastBoxList = None
            self.stackManager.view.Refresh()
        elif self.mode == "move":
            pos = self.targetUi.model.GetProperty("position")
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
                    m.SetProperty("position", viewOrigin, notify=False)
                self.stackManager.command_processor.Submit(command)
        elif self.mode == "rotate":
            newRot = self.targetUi.model.GetProperty("rotation")
            self.stackManager.view.Freeze()
            self.targetUi.model.SetProperty("rotation", self.origRotation)
            command = SetPropertyCommand(True, "Set Rotation", self.stackManager.designer.cPanel,
                                         self.stackManager.cardIndex, self.targetUi.model,
                                         "rotation", newRot)
            self.stackManager.command_processor.Submit(command)
            self.stackManager.view.Thaw()
        elif self.mode == "resize":
            pos = self.targetUi.model.GetProperty("position")
            viewOrigin = self.oldFrames[self.targetUi.model.GetProperty("name")].Position
            moveOffset = (pos[0] - viewOrigin.x, pos[1] - viewOrigin.y)

            endw, endh = self.targetUi.model.GetProperty("size")
            origSize = self.oldFrames[self.targetUi.model.GetProperty("name")].Size
            sizeOffset = (endw-origSize[0], endh-origSize[1])

            if moveOffset != (0, 0) or sizeOffset != (0, 0):
                commands = []
                commands.append(ResizeUiViewCommand(True, 'Resize-Resize', self.stackManager,
                                                    self.stackManager.cardIndex,
                                                    self.targetUi.model, sizeOffset))
                if self.targetUi.model.type != "card":
                    commands.append(MoveUiViewsCommand(True, 'Resize-Move', self.stackManager,
                                                       self.stackManager.cardIndex,
                                                       [self.targetUi.model], moveOffset))
                if self.xFlipped or self.yFlipped:
                    self.targetUi.model.PerformFlips(self.xFlipped, self.yFlipped, notify=False)  # First unflip
                    commands.append(FlipShapeCommand(True, 'Resize-Flip', self.stackManager,
                                                     self.stackManager.cardIndex,
                                                     self.targetUi.model, self.xFlipped, self.yFlipped))

                self.stackManager.view.Freeze()
                self.targetUi.model.SetProperty("position", viewOrigin, notify=False)
                self.targetUi.model.SetProperty("size", origSize, notify=False)
                command = CommandGroup(True, "Resize", self, commands)
                self.stackManager.command_processor.Submit(command)
                self.stackManager.view.Thaw()

        self.mode = None
        self.stackManager.view.SetFocus()
        self.targetUi = None
        self.resizeCorner = None
        self.resizeAnchorPointLocal = None
        self.resizeAnchorPointAbs = None
        self.resizeCardLastSize = None
        self.resizeAff = None
        self.resizeAffInverted = None
        self.origRotation = None
        event.Skip()

    def UpdateBoxSelection(self):
        uiList = []
        for ui in self.stackManager.uiCard.uiViews:
            if self.selectionRect.Contains(tuple((int(x) for x in ui.model.GetCenter()))):
                uiList.append(ui)
        if uiList != self.lastBoxList:
            self.stackManager.SelectUiView(None)
            for ui in uiList:
                self.stackManager.SelectUiView(ui, True)
            self.lastBoxList = uiList

    def OnKeyDown(self, uiViewIn, event):
        if event.RawControlDown() or event.CmdDown():
            event.Skip()
            return

        uiViews = []
        if uiViewIn and uiViewIn.model.type == "card":
            uiViews = self.stackManager.GetSelectedUiViews()

        code = event.GetKeyCode()

        if code in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE, wx.WXK_BACK]:
            self.stackManager.DeleteModels([ui.model for ui in uiViews])
            return

        if code == wx.WXK_TAB:
            allUiViews = self.stackManager.uiCard.GetAllUiViews()
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
            return

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
                if pos.x + sharedFrame.Width - dist < 2: dist = pos.x + sharedFrame.Width - 2
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (-dist, 0))
            elif code == wx.WXK_RIGHT:
                if pos.x+dist > cardRect.Right-2: dist = cardRect.Right-2 - pos.x
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (dist, 0))
            elif code in [wx.WXK_UP, wx.WXK_NUMPAD_UP]:
                if pos.y+dist > cardRect.Bottom-2: dist = cardRect.Bottom-2 - pos.y
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (0, dist))
            elif code in [wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN]:
                if pos.y + sharedFrame.Height - dist < 2: dist = pos.y + sharedFrame.Height - 2
                if dist > 0:
                    command = MoveUiViewsCommand(True, 'Move', self.stackManager, self.stackManager.cardIndex, models, (0, -dist))

            if command:
                self.stackManager.command_processor.Submit(command)


class ViewTool(BaseTool):
    """
    The View tool allows creating Buttons, Text Fields, Text labels, and Images.
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
            pos = self.ConstrainDragPoint(self.name, self.origMousePos, event)

            if not self.targetUi and dist(self.origMousePos, pos) > MOVE_THRESHOLD:
                m = generator.StackGenerator.ModelFromType(self.stackManager, self.name)
                m.SetProperty("size", [0,0], notify=False)
                m.SetProperty("position", self.origMousePos, notify=False)
                self.targetUi = self.stackManager.AddUiViewInternal(m)
                self.stackManager.SelectUiView(self.targetUi)

            if self.targetUi:
                offset = (pos.x-self.origMousePos[0], pos.y-self.origMousePos[1])
                topLeft = (min(pos[0], self.origMousePos[0]), min(pos[1], self.origMousePos[1]))
                self.targetUi.model.SetProperty("position", topLeft, notify=False)
                self.targetUi.model.SetProperty("size", [abs(offset[0]), abs(offset[1])])
        event.Skip()

    def OnMouseUp(self, uiView, event):
        if self.stackManager.view.HasCapture():
            self.stackManager.view.ReleaseMouse()
            if self.targetUi:
                endw, endh = self.targetUi.model.GetProperty("size")
                offset = (endw, endh)
                if offset != (0, 0):
                    model = self.targetUi.model
                    self.stackManager.view.Freeze()
                    command = AddNewUiViewCommand(True, 'Add View', self.stackManager, self.stackManager.cardIndex, model.type, model)
                    self.stackManager.RemoveUiViewByModel(model)
                    model.SetBackUp(self.stackManager)
                    self.stackManager.command_processor.Submit(command)
                    self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
                    self.stackManager.view.Thaw()
                self.stackManager.view.SetFocus()
                self.targetUi = None
                self.stackManager.designer.cPanel.SetToolByName("hand")


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
        self.pen_color = None
        self.targetUi = None

    def SetPenColor(self, color):
        self.pen_color = color

    def SetFillColor(self, color):
        pass

    def SetThickness(self, num):
        self.thickness = num

    def OnMouseDown(self, uiView, event):
        self.pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))

        m = generator.StackGenerator.ModelFromType(self.stackManager, self.name)
        m.SetProperty("position", [0,0], notify=False)
        m.SetProperty("size", self.stackManager.stackModel.GetProperty("size"))
        self.targetUi = self.stackManager.AddUiViewInternal(m)
        # self.stackManager.SelectUiView(self.targetUi)

        self.stackManager.view.CaptureMouse()
        self.curLine = []
        self.curLine.append(list(self.pos))
        self.targetUi.model.SetShape({"type": "pen", "pen_color": self.pen_color, "thickness": self.thickness, "points": self.curLine})

    def OnMouseMove(self, uiView, event):
        if self.targetUi and self.stackManager.view.HasCapture():
            pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
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

            self.stackManager.view.Freeze()
            model.ReCropShape()

            command = AddNewUiViewCommand(True, 'Add Shape', self.stackManager, self.stackManager.cardIndex, model.type, model)
            self.stackManager.RemoveUiViewByModel(model)
            model.SetBackUp(self.stackManager)
            self.stackManager.command_processor.Submit(command)
            self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
            self.stackManager.view.Thaw()
            self.stackManager.designer.cPanel.SetToolByName("hand")
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
        self.pen_color = None
        self.fill_color = None
        self.targetUi = None

    def SetPenColor(self, color):
        self.pen_color = color

    def SetFillColor(self, color):
        self.fill_color = color

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
                m = generator.StackGenerator.ModelFromType(self.stackManager, self.name)
                m.SetProperty("position", [0, 0], notify=False)
                m.SetProperty("size", self.stackManager.stackModel.GetProperty("size"), notify=False)
                m.SetShape({"type": self.name, "pen_color": self.pen_color, "fill_color": self.fill_color,
                            "thickness": self.thickness, "points": self.points})
                self.targetUi = self.stackManager.AddUiViewInternal(m)
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

                self.stackManager.view.Freeze()
                model.ReCropShape()

                command = AddNewUiViewCommand(True, 'Add Shape', self.stackManager, self.stackManager.cardIndex, model.type, model)
                self.stackManager.RemoveUiViewByModel(model)
                model.SetBackUp(self.stackManager)
                self.stackManager.command_processor.Submit(command)
                self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
                self.stackManager.view.Thaw()
                self.stackManager.designer.cPanel.SetToolByName("hand")
        self.stackManager.view.SetFocus()


class PolygonTool(BaseTool):
    """
    The Polygon tool allows drawing polygons.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.cursor = wx.CURSOR_CROSS
        self.name = "polygon"
        self.points = None
        self.thickness = 0
        self.pen_color = None
        self.fill_color = None
        self.targetUi = None
        self.mouse_pos = None
        self.lastMousePos = None

    def SetPenColor(self, color):
        self.pen_color = color

    def SetFillColor(self, color):
        self.fill_color = color

    def SetThickness(self, num):
        self.thickness = num

    def OnMouseDown(self, uiView, event):
        mouse_pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
        if not self.stackManager.view.HasCapture():
            self.points = [mouse_pos]
            m = generator.StackGenerator.ModelFromType(self.stackManager, self.name)
            m.SetProperty("position", [0, 0], notify=False)
            m.SetProperty("size", self.stackManager.stackModel.GetProperty("size"), notify=False)
            m.SetShape({"type": self.name, "pen_color": self.pen_color, "fill_color": self.fill_color,
                        "thickness": self.thickness, "points": self.points})
            self.targetUi = self.stackManager.AddUiViewInternal(m)
            self.stackManager.view.CaptureMouse()
        elif dist(mouse_pos, self.points[0]) < 5:
            self.FinishShape()
        elif dist(mouse_pos, self.points[-1]) < 5:
            self.FinishShape()
        else:
            self.points.append(self.ConstrainDragPoint("line", self.points[-1], event))
            self.targetUi.model.DidUpdateShape()

    def OnMouseMove(self, uiView, event):
        self.mouse_pos = self.stackManager.view.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))

        if self.stackManager.view.HasCapture():
            if wx.GetMouseState().LeftIsDown():
                if self.points and len(self.points)>1:
                    self.mouse_pos = self.ConstrainDragPoint("line", self.points[-2], event)
                self.points[-1] = self.mouse_pos
                self.targetUi.model.DidUpdateShape()
            else:
                if len(self.points) >= 1:
                    if self.points and len(self.points):
                        self.mouse_pos = self.ConstrainDragPoint("line", self.points[-1], event)
                    points = [self.points[0], self.points[-1], self.mouse_pos]
                    if self.lastMousePos:
                        points.append(self.lastMousePos)
                    self.targetUi.model.DidUpdateShape()
                    self.lastMousePos = self.mouse_pos

    def OnMouseUp(self, uiView, event):
        pass

    def Paint(self, gc):
        if self.stackManager.view.HasCapture() and len(self.points) >= 1 and self.mouse_pos:
            gc.SetPen(wx.Pen('Blue', 2, wx.PENSTYLE_DOT))
            gc.DrawLine(self.points[0], self.mouse_pos)
            gc.DrawLine(self.points[-1], self.mouse_pos)

    def OnKeyDown(self, uiViewIn, event):
        if event.RawControlDown() or event.CmdDown():
            event.Skip()
            return

        code = event.GetKeyCode()

        if self.stackManager.view.HasCapture():
            if code in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_ESCAPE]:
                self.FinishShape()
            elif code in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE, wx.WXK_BACK]:
                if len(self.points) > 1:
                    del self.points[-1]
                self.targetUi.model.DidUpdateShape()

    def Deactivate(self):
        if self.stackManager.view.HasCapture():
            self.FinishShape()

    def FinishShape(self):
        self.stackManager.view.ReleaseMouse()
        if self.targetUi:
            model = self.targetUi.model
            self.targetUi = None

            model.ReCropShape()

            self.stackManager.view.Freeze()
            if len(self.points) >= 3:
                command = AddNewUiViewCommand(True, 'Add Shape', self.stackManager, self.stackManager.cardIndex, model.type, model)
                self.stackManager.RemoveUiViewByModel(model)
                model.SetBackUp(self.stackManager)
                self.stackManager.command_processor.Submit(command)
                self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(model))
            else:
                self.stackManager.RemoveUiViewByModel(model)
            self.stackManager.view.Thaw()

            self.stackManager.designer.cPanel.SetToolByName("hand")
        self.points = None
        self.mouse_pos = None
        self.lastMousePos = None
        self.stackManager.view.SetFocus()
