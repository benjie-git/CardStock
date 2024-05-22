# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import threading
import ast
import re
from easing import ease
import generator
import helpDataGen
from time import time
from codeRunnerThread import RunOnMainSync, RunOnMainAsync
from cardstockFrameParts import *
import sanitizer
import math
from imageFactory import ImageFactory


class UiView(object):
    """
    This class is an abstract base class for the other Ui objects (view controllers) that coordinate management of
    their views and models.
    """

    def __init__(self, parent, stackManager, model, view):
        super().__init__()
        self.stackManager = stackManager
        self.parent = parent
        self.uiViews = []
        self.view = view
        self.model = None
        self.SetModel(model)
        self.hitRegion = None
        self.isSelected = False
        self.hasMouseMoved = False
        self.SetView(view)

        self.lastEditedHandler = None
        self.delta = ((0, 0))

    def __repr__(self):
        if self.model:
            return "<"+str(self.__class__.__name__) + ":" + self.model.type + ":'" + self.model.GetProperty("name")+"'>"
        return "<"+str(self.__class__.__name__)+">"

    def SetDown(self):
        for ui in self.uiViews:
            ui.SetDown()
        self.DestroyView()
        self.stackManager = None
        self.parent = None
        self.uiViews = None
        self.model = None
        self.hitRegion = None

    def BindEvents(self, view):
        view.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        view.Bind(wx.EVT_LEFT_DCLICK, self.FwdOnMouseDown)
        view.Bind(wx.EVT_RIGHT_DOWN, self.FwdOnRightDown)
        view.Bind(wx.EVT_MOTION, self.FwdOnMouseMove)
        view.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseUp)
        view.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        view.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

    def FwdOnRightDown( self, event): self.stackManager.OnRightDown( self, event)
    def FwdOnMouseDown( self, event): self.stackManager.OnMouseDown( self, event)
    def FwdOnMouseMove( self, event): self.stackManager.OnMouseMove( self, event)
    def FwdOnMouseUp(   self, event): self.stackManager.OnMouseUp(   self, event)
    def FwdOnKeyDown(   self, event): self.stackManager.OnKeyDown(   self, event)
    def FwdOnKeyUp(     self, event): self.stackManager.OnKeyUp(     self, event)

    def SetView(self, view):
        self.view = view
        if view:
            if self.GetCursor():
                self.view.SetCursor(wx.Cursor(self.GetCursor()))

            s = self.model.GetProperty("size")
            if s[0] > 0 and s[1] > 0:
                if self.model.type in ("stack", "card"):
                    if self.stackManager.uiCard:
                        self.stackManager.uiCard.ResizeCardView(s)
                    pos = (0,0)
                else:
                    c = self.stackManager.ConvPoint(wx.Point(self.model.GetCenter()))
                    s = self.view.FromDIP(self.model.GetProperty("size"))
                    pos = c - s / 2
                    self.view.SetSize(s)
                self.view.SetPosition(pos)

            self.BindEvents(view)
            view.Bind(wx.EVT_SIZE, self.OnResize)
            self.view.Show(self.model.IsVisible())

    def SetModel(self, model):
        self.model = model
        self.lastEditedHandler = None

    def GetCursor(self):
        if self.stackManager.isEditing:
            return wx.CURSOR_HAND
        else:
            return None

    def OnPropertyChanged(self, model, key):
        if key in ["position", "size", "rotation"]:
            if self.view:
                s = model.GetProperty("size")
                if model.type == "card":
                    self.stackManager.uiCard.ResizeCardView(s)
                    pos = (0,0)
                else:
                    c = self.stackManager.ConvPoint(wx.Point(model.GetCenter()))
                    s = self.view.FromDIP(model.GetProperty("size"))
                    pos = c - s / 2
                    self.view.SetSize(s)
                self.view.SetPosition(pos)
                self.view.Refresh()
            if key == "position":
                # If we're just moving the object, we don't need to rebuild the hit region, just offset it
                self.MoveHitRegion()
            else:
                self.ClearHitRegion()
            self.stackManager.view.Refresh()
        elif key == "is_visible":
            if self.view:
                self.view.Show(self.model.IsVisible())
            self.stackManager.view.Refresh()

    def OnResize(self, event):
        pass

    def DestroyView(self):
        if self.view:
            if self.view.HasCapture():
                self.view.ReleaseMouse()
            if self.view.GetParent() == self.stackManager.view:
                self.stackManager.view.RemoveChild(self.view)
            self.view.Destroy()
            self.view = None

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        if self.isSelected != selected:
            self.isSelected = selected
            self.ClearHitRegion()
            self.stackManager.view.Refresh()

    def OnMouseDown(self, event):
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_mouse_press"):
            self.stackManager.runner.RunHandler(self.model, "on_mouse_press", event)
        event.Skip()

    def OnMouseMove(self, event):
        self.hasMouseMoved = True
        event.Skip()

    def OnMouseUpOutside(self, event):
        pass

    def OnMouseUp(self, event):
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_mouse_release"):
            self.stackManager.runner.RunHandler(self.model, "on_mouse_release", event)
        event.Skip()

    def OnMouseEnter(self, event):
        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_mouse_enter"):
            self.stackManager.runner.RunHandler(self.model, "on_mouse_enter", event)
        event.Skip()

    def OnMouseExit(self, event):
        self.hasMouseMoved = False
        if self.stackManager and not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_mouse_exit"):
            self.stackManager.runner.RunHandler(self.model, "on_mouse_exit", event)
        event.Skip()

    def RunAnimations(self, onFinishedCalls, elapsed_time):
        # Move the object by speed.x and speed.y pixels per second
        updateList = []
        finishList = []
        didRun = False
        with self.model.animLock:
            if self.model.type not in ["stack", "card"]:
                speed = self.model.properties["speed"]
                if speed != (0,0) and "position" not in self.model.animations:
                    pos = self.model.properties["position"]
                    self.model.SetProperty("position", [pos.x + speed.x*elapsed_time, pos.y + speed.y*elapsed_time])
                    didRun = True

            # Run any in-progress animations
            now = time()
            for (key, animList) in self.model.animations.items():
                animDict = animList[0]
                if "startTime" in animDict:
                    progress = (now - animDict["startTime"]) / animDict["duration"]
                    if progress < 1.0:
                        if animDict["onUpdate"]:
                            updateList.append([animDict, progress])
                    else:
                        if animDict["onUpdate"]:
                            updateList.append([animDict, 1.0])
                        finishList.append(key)
        for (d,p) in updateList:
            d["onUpdate"](p, d)
            didRun = True
        for key in finishList:
            def deferFinish(key):
                def f(): self.model.FinishAnimation(key)
                return f
            onFinishedCalls.append(deferFinish(key))
        return didRun

    def FindCollisions(self, collisions):
        # Find collisions between this object and others in its bounceObjs list
        # and add them to the collisions list, to be handled after all are found.
        removeFromBounceObjs = []
        if not self.model.didSetDown and self.model.GetProperty("is_visible") and tuple(self.model.GetProperty("speed")) != (0, 0):
            for k,v in self.model.bounceObjs.items():
                other_ui = self.stackManager.GetUiViewByModel(k)
                (mode, last_dist) = v

                if not other_ui.model.GetProperty("is_visible"):
                    continue

                if other_ui.model.didSetDown:
                    # remove deleted objects from the bounceObjs list, after this loop is done
                    removeFromBounceObjs.append(k)
                    continue

                sc = self.model.GetProxy().center       # sc = self center
                oc = other_ui.model.GetProxy().center   # oc = other center
                new_dist = (abs(sc[0]-oc[0]), abs(sc[1]-oc[1]))

                if not mode:
                    # Determine whether we're inside or outside of this object
                    self.model.bounceObjs[k][0] = "In" if other_ui.model.GetProxy().is_touching_point(self.model.GetCenter()) else "Out"
                    self.model.bounceObjs[k][1] = new_dist
                    continue

                edges = self.model.GetProxy().is_touching_edge(other_ui.model.GetProxy(), mode == "In")
                if mode == "In" and not edges:
                    if not other_ui.model.GetProxy().is_touching_point(self.model.GetCenter()):
                        edges = []
                        sc = self.model.GetCenter()
                        oc = other_ui.model.GetCenter()
                        if sc[0] < oc[0]: edges.append("Left")
                        if sc[0] > oc[0]: edges.append("Right")
                        if sc[1] < oc[1]: edges.append("Bottom")
                        if sc[1] > oc[1]: edges.append("Top")
                if edges:
                    selfBounceAxes = ""
                    otherBounceAxes = ""
                    ss = self.model.GetProxy().speed
                    os = other_ui.model.GetProxy().speed
                    if mode == "In":
                        # Bounce if hitting an edge of the enclosing object, and only if moving toward the other object's edge
                        if ("Left" in edges or "Right" in edges) and new_dist[0] > last_dist[0]:
                            if (ss[0] > 0 and oc[0] < sc[0]) or (ss[0] < 0 and oc[0] > sc[0]):
                                selfBounceAxes += "H"
                            if (os[0] > 0 and sc[0] < oc[0]) or (os[0] < 0 and sc[0] > oc[0]):
                                otherBounceAxes += "H"
                        if ("Top" in edges or "Bottom" in edges) and new_dist[1] > last_dist[1]:
                            if (ss[1] > 0 and oc[1] < sc[1]) or (ss[1] < 0 and oc[1] > sc[1]):
                                selfBounceAxes += "V"
                            if (os[1] > 0 and sc[1] < oc[1]) or (os[1] < 0 and sc[1] > oc[1]):
                                otherBounceAxes += "V"
                    elif mode == "Out":
                        # Bounce if hitting an edge of the other object, and only if moving toward the other object
                        if ("Left" in edges or "Right" in edges) and new_dist[0] < last_dist[0]:
                            if (ss[0] > 0 and oc[0] > sc[0]) or (ss[0] < 0 and oc[0] < sc[0]):
                                selfBounceAxes += "H"
                            if (os[0] > 0 and sc[0] > oc[0]) or (os[0] < 0 and sc[0] < oc[0]):
                                otherBounceAxes += "H"
                        if ("Top" in edges or "Bottom" in edges) and new_dist[1] < last_dist[1]:
                            if (ss[1] > 0 and oc[1] > sc[1]) or (ss[1] < 0 and oc[1] < sc[1]):
                                selfBounceAxes += "V"
                            if (os[1] > 0 and sc[1] > oc[1]) or (os[1] < 0 and sc[1] < oc[1]):
                                otherBounceAxes += "V"

                    if len(selfBounceAxes) or len(otherBounceAxes):
                        sn = self.model.GetProperty("name")
                        on = other_ui.model.GetProperty("name")
                        key = (self, other_ui) if sn < on else (other_ui, self)
                        if key not in collisions:
                            # Add this collision to the list, indexed by normalized object pair to avoid duplicates
                            edgeList = []
                            for eStr in ("Top", "Bottom", "Left", "Right"):
                                if eStr in edges: edgeList.append(eStr)
                            collisions[key] = (self, other_ui, selfBounceAxes, otherBounceAxes, tuple(edgeList), mode)

                self.model.bounceObjs[k][1] = new_dist

            for k in removeFromBounceObjs:
                del self.model.bounceObjs[k]

    def PerformBounce(self, info, elapsed_time):
        # Perform this bounce for this object, and the other object
        (this_ui, other_ui, selfAxes, otherAxes, edges, mode) = info
        ss = self.model.GetProxy().speed
        os = other_ui.model.GetProxy().speed

        # Flags
        selfBounce = other_ui.model in self.model.bounceObjs
        selfBounceInside = False if not selfBounce else self.model.bounceObjs[other_ui.model][0] == "In"
        otherBounce = self.model in other_ui.model.bounceObjs

        # Back up to avoid overlap
        self.model.SetProperty("position", self.model.GetProperty("position") - tuple(ss*(elapsed_time/2)))

        # Finally perform the actual bounces
        if selfBounce and "H" in selfAxes:
            ss.x = -ss.x
        if otherBounce and "H" in otherAxes:
            os.x = -os.x
        if selfBounce and "V" in selfAxes:
            ss.y = -ss.y
        if otherBounce and "V" in otherAxes:
            os.y = -os.y

        # Call the bounce handlers.  It's possible to bounce off of 2 edges at once (a corner), in which
        # case we call this handler once per edge it bounced off of.
        if other_ui.model in self.model.bounceObjs:
            for edge in edges:
                if self.stackManager.runner and self.model.GetHandler("on_bounce"):
                    self.stackManager.runner.RunHandler(self.model, "on_bounce", None,
                                                        [other_ui.model.GetProxy(), edge])

        if self.model in other_ui.model.bounceObjs:
            # Use this opposites dict to show the right edge names in the other object's on_bounce calls
            opposites = {"Top": "Bottom", "Bottom": "Top", "Left": "Right", "Right": "Left"}
            for edge in edges:
                otherEdge = edge if selfBounceInside else opposites[edge] # Don't flip names for inside bounces
                if self.stackManager.runner and other_ui.model.GetHandler("on_bounce"):
                    self.stackManager.runner.RunHandler(other_ui.model, "on_bounce", None,
                                                        [self.model.GetProxy(), otherEdge])

    def OnPeriodic(self, event):
        if self.stackManager.isEditing:
            return

        didRun = False
        if self.hasMouseMoved:
            self.hasMouseMoved = False
            if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_mouse_move"):
                self.stackManager.runner.RunHandler(self.model, "on_mouse_move", event)
                didRun = True

        if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_periodic"):
            self.stackManager.runner.RunHandler(self.model, "on_periodic", event)
            didRun = True

        return didRun

    def DoPaint(self, gc):
        # Recursively paint this object and all children
        self.PrePaint(gc)
        if self.model.IsVisible():
            self.Paint(gc)
            for ui in self.uiViews:
                ui.DoPaint(gc)
        self.PostPaint(gc)

    def DoPaintSelectionBoxes(self, gc):
        # Recursively paint selection boxes for this object and all children, if selected
        self.PrePaint(gc)
        if self.isSelected:
            self.PaintSelectionBox(gc)
        for ui in self.uiViews:
            ui.DoPaintSelectionBoxes(gc)
        self.PostPaint(gc)

    def PrePaint(self, gc):
        # Rotate and Translate the GC, such that we can draw this object in local coords
        stackSize = self.stackManager.uiCard.model.GetProperty("size")
        pos = self.model.properties["position"]
        rot = self.model.GetProperty("rotation")
        rot = math.radians(rot) if rot else None
        gc.cachedGC.PushState()
        scale = self.stackManager.view.FromDIP(1000)/1000.0

        if rot:
            cen = self.model.properties["size"] / 2
            gc.cachedGC.Translate(scale*(pos[0] + cen[0]), scale*(stackSize.height - (pos[1] + cen[1])))
            gc.cachedGC.Rotate(rot)
            gc.cachedGC.Translate(scale*(-cen[0]), scale*(cen[1] - stackSize.height))
        else:
            gc.cachedGC.Translate(scale*pos[0], -pos[1]*scale)


    def Paint(self, gc):
        self.PaintBoundingBox(gc)

    def PaintBoundingBox(self, gc, color='Gray'):
        if self.stackManager.isEditing:
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(color, self.stackManager.view.FromDIP(1), wx.PENSTYLE_DOT))

            pos = wx.Point(0,0)-[int(x) for x in self.model.GetProperty("position")]
            f = self.model.GetFrame()
            f.Offset(pos)
            gc.DrawRectangle(f)

    def PaintSelectionBox(self, gc):
        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            pos = wx.Point(0,0)-[int(x) for x in self.model.GetProperty("position")]
            f = self.model.GetFrame()
            f.Offset(pos)

            gc.SetPen(wx.Pen('Blue', self.stackManager.view.FromDIP(3), wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Inflate(2))

            if self.model.parent and self.model.parent.type != "group":
                gc.SetPen(wx.TRANSPARENT_PEN)
                gc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_SOLID))
                for box in self.GetLocalResizeBoxRects().values():
                    gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))
                rotPt = self.GetLocalRotationHandlePoint()
                if rotPt:
                    gc.DrawCircle(rotPt, 6)

    def PostPaint(self, gc):
        # Un-transform the coordinate system after drawing this object
        gc.cachedGC.PopState()

    def HitTest(self, pt):
        f = self.model.GetAbsoluteFrame()
        inflate = 20
        if "pen_thickness" in self.model.properties:
            inflate += self.model.properties["pen_thickness"]
        f.Inflate(int(inflate))
        if f.Contains(pt):
            if not self.hitRegion:
                self.MakeHitRegion()
            if self.hitRegion.Contains(pt):
                return self
        return None

    def HasGroupAncestor(self, uiView):
        ui = self
        while ui and ui.model.type not in ["card", "stack"]:
            if ui == uiView:
                return True
            ui = ui.parent
        return False

    def GetLocalResizeBoxPoints(self):
        # Define the local coords of the centers of the resize boxes.
        # These are used to generate rotated points, and rects for resize boxes.
        # The resize box/handles should hang out of the frame, to allow grabbing it from behind
        # native widgets which can obscure the full frame.
        # Return as a dict, so each point is labelled, for use when dragging to resize
        s = self.model.GetProperty("size")
        return {"BL":wx.Point(0,0), "BR": wx.Point(s.width+4,0), "TL": wx.Point(0,s.height+4), "TR": wx.Point(s.width+4, s.height+4)}

    def GetResizeBoxPoints(self):
        points = self.GetLocalResizeBoxPoints()
        aff = self.model.GetAffineTransform()
        return {k:wx.Point(tuple(int(x) for x in aff.TransformPoint(*p))) for k,p in points.items()}

    def GetResizeBoxRects(self):
        points = self.GetResizeBoxPoints()
        return {k:wx.Rect(p.x-6, p.y-6, 12, 12) for k,p in points.items()}

    def GetLocalResizeBoxRects(self):
        points = self.GetLocalResizeBoxPoints()
        return {k:wx.Rect(p.x-6, p.y-6, 12, 12) for k,p in points.items()}

    def GetLocalRotationHandlePoint(self):
        points = self.GetLocalResizeBoxPoints()
        if "rotation" in self.model.properties and "TR" in points and "TL" in points:
            return ((points["TR"] + points["TL"])/2 + (0, 10))
        return None

    def GetRotationHandlePoint(self):
        aff = self.model.GetAffineTransform()
        pt = self.GetLocalRotationHandlePoint()
        if pt:
            return aff.TransformPoint(*pt)
        return None

    def ClearHitRegion(self, noParent=False):
        self.hitRegion = None
        if self.parent and noParent == False and self.parent.model.type == "group":
            self.parent.ClearHitRegion()

    def GetHitRegion(self):
        if not self.hitRegion:
            self.MakeHitRegion()
        return self.hitRegion

    def MoveHitRegion(self):
        if self.hitRegion:
            oldPos = self.hitRegionOffset
            newPos = self.model.GetAbsolutePosition()
            self.hitRegion.Offset(wx.Point(newPos-oldPos))
            self.hitRegionOffset += tuple(wx.Point(newPos-oldPos))
            if self.parent and self.parent.model.type == "group":
                self.parent.ClearHitRegion()

    def MakeHitRegion(self):
        # Make a region in absolute/card coordinates
        if not self.model.IsVisible():
            self.hitRegion = wx.Region((0,0), (0,0))

        s = self.model.GetProperty("size")
        rect = wx.Rect(0, 0, s.Width + 1, s.Height + 1)
        points = self.model.RotatedRectPoints(rect)
        points.append(points[0])

        l2 = list(map(list, zip(*points)))
        rotSize = (max(l2[0]) - min(l2[0]) - 1, max(l2[1]) - min(l2[1]) - 1)
        rotPos_x, rotPos_y = (min(l2[0]), min(l2[1]))

        # Draw the region offset up/right, to allow space for bottom/left resize boxes,
        # since they would otherwise be at negative coords, which would be outside the
        # hitRegion bitmap.  Then set the offset of the hitRegion bitmap down/left to make up for it.
        regOffset = 20

        img = ImageFactory.shared().GetImage(rotSize[0]+2*regOffset, rotSize[1]+2*regOffset)
        context = wx.GraphicsRenderer.GetDefaultRenderer().CreateContextFromImage(img)
        context.SetBrush(wx.Brush('white', wx.BRUSHSTYLE_SOLID))

        aff = self.model.GetAffineTransform()
        vals = aff.Get()
        # Draw into region bmp rotated but not translated
        vals = (vals[0].m_11, vals[0].m_12, vals[0].m_21, vals[0].m_22, vals[1][0] - (rotPos_x-regOffset), vals[1][1] - (rotPos_y-regOffset))
        aff = context.CreateMatrix(*vals)

        path = context.CreatePath()
        p1 = rect.TopLeft
        p2 = rect.BottomRight
        path.AddRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
        path.Transform(aff)
        context.FillPath(path)

        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            for resizerRect in self.GetLocalResizeBoxRects().values():
                path = context.CreatePath()
                path.AddRectangle(resizerRect.Left, resizerRect.Top-2, resizerRect.Width, resizerRect.Height)
                path.Transform(aff)
                context.FillPath(path)
            rotPt = self.GetLocalRotationHandlePoint()
            if rotPt:
                path = context.CreatePath()
                path.AddCircle(*[int(x) for x in rotPt], 6)
                path.Transform(aff)
                context.FillPath(path)
        context.Flush()

        reg = img.ConvertToRegion(0,0,0)
        ImageFactory.shared().RecycleImage(img)
        reg.Offset(int(rotPos_x-regOffset), int(rotPos_y-regOffset))
        self.hitRegion = reg
        self.hitRegionOffset = self.model.GetAbsolutePosition()

    def MakeRegionFromLocalRect(self, rect):
        # Make a region in absolute/card coordinates
        points = self.model.RotatedRectPoints(rect)
        points.append(points[0])

        l2 = list(map(list, zip(*points)))
        rotSize = (max(l2[0]) - min(l2[0]), max(l2[1]) - min(l2[1]))
        rotPos_x, rotPos_y = (min(l2[0]), min(l2[1]))

        img = ImageFactory.shared().GetImage(*rotSize)
        context = wx.GraphicsRenderer.GetDefaultRenderer().CreateContextFromImage(img)
        context.SetBrush(wx.Brush('white', wx.BRUSHSTYLE_SOLID))

        aff = self.model.GetAffineTransform()
        vals = aff.Get()
        # Draw into region bmp rotated but not translated
        vals = (vals[0].m_11, vals[0].m_12, vals[0].m_21, vals[0].m_22, vals[1][0] - (rotPos_x), vals[1][1] - (rotPos_y))
        aff = context.CreateMatrix(*vals)

        path = context.CreatePath()
        p1 = rect.TopLeft
        p2 = rect.BottomRight
        path.AddRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
        path.Transform(aff)
        context.FillPath(path)
        context.Flush()

        reg = img.ConvertToRegion(0,0,0)
        ImageFactory.shared().RecycleImage(img)
        reg.Offset(rotPos_x, rotPos_y)
        return reg

    handlerDisplayNames = {
        'on_setup':      "on_setup(self):",
        'on_show_card':   "on_show_card(self):",
        'on_hide_card':   "on_hide_card(self):",
        'on_click':      "on_click(self):",
        'on_selection_changed': "on_selection_changed(self, is_selected):",
        'on_text_enter':  "on_text_enter(self):",
        'on_text_changed':"on_text_changed(self):",
        'on_mouse_press': "on_mouse_press(self, mouse_pos):",
        'on_mouse_move':  "on_mouse_move(self, mouse_pos):",
        'on_mouse_release':"on_mouse_release(self, mouse_pos):",
        'on_mouse_enter': "on_mouse_enter(self, mouse_pos):",
        'on_mouse_exit':  "on_mouse_exit(self, mouse_pos):",
        'on_done_loading':"on_done_loading(self, URL, did_load):",
        'on_card_stock_link':"on_card_stock_link(self, message):",
        'on_bounce':     "on_bounce(self, other_object, edge):",
        'on_message':    "on_message(self, message):",
        'on_key_press':   "on_key_press(self, key_name):",
        'on_key_hold':    "on_key_hold(self, key_name, elapsed_time):",
        'on_key_release': "on_key_release(self, key_name):",
        'on_resize':     "on_resize(self, is_initial):",
        'on_periodic':   "on_periodic(self, elapsed_time):",
        'on_exit_stack':  "on_exit_stack(self):",
    }


class ViewModel(object):
    """
    This is the abstract base class for the other model classes.
    The model holds the property values and event handler text for each object.
    It also holds the type of each property, and the ordered list of properties to display in the inspector.
    It also handles animating properties of the object, like position, size, or color.
    """

    minSize = wx.Size(20, 20)
    reservedNames = helpDataGen.HelpData.ReservedNames()

    def __init__(self, stackManager):
        super().__init__()
        self.type = None
        self.parent = None
        self.handlers = {"on_setup": "",
                         "on_mouse_enter": "",
                         "on_mouse_press": "",
                         "on_mouse_move": "",
                         "on_mouse_release": "",
                         "on_mouse_exit": "",
                         "on_bounce": "",
                         "on_message": "",
                         "on_periodic": ""
                         }
        self.initialEditHandler = "on_mouse_press"
        self.visibleHandlers = set()

        self.properties = {"name": "",
                           "size": wx.Size(0,0),
                           "position": wx.RealPoint(0,0),
                           "speed": wx.Point(0,0),
                           "is_visible": True,
                           "data": {}
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "floatpoint",
                              "center": "floatpoint",
                              "size": "size",
                              "speed": "point",
                              "is_visible": "bool",
                              "data": "dict"
                              }

        self.childModels = []
        self.stackManager = stackManager
        self.isDirty = False
        self.proxy = None
        self.lastOnPeriodicTime = None
        self.animations = {}
        self.bounceObjs = {}
        self.proxyClass = ViewProxy
        self.animLock = threading.Lock()
        self.didSetDown = False
        self.didDelete = False
        self.clonedFrom = None

    def __repr__(self):
        return f"<{self.GetDisplayType()}:'{self.GetProperty('name')}'>"

    def SetBackUp(self, stackManager):
        if self.didSetDown:
            self.stackManager = stackManager
            self.didSetDown = False
            for child in self.childModels:
                child.SetBackUp(stackManager)
                child.parent = self

    def SetDown(self):
        with self.animLock:
            self.didSetDown = True
            for child in self.childModels:
                child.SetDown()
            if self.proxy:
                self.proxy._model = None
                self.proxy = None
            self.animations = {}
            self.bounceObjs = {}
            self.stackManager = None
            self.parent = None

    def DismantleChildTree(self):
        for child in self.childModels:
            child.DismantleChildTree()
        self.childModels = None

    def CreateCopy(self, name=None):
        data = self.GetData()
        newModel = generator.StackGenerator.ModelFromData(self.stackManager, data)
        newModel.clonedFrom = self.clonedFrom if self.clonedFrom else self
        if newModel.type != "card":
            if name:
                newModel.properties["name"] = name
            self.stackManager.uiCard.model.DeduplicateNamesForModels([newModel])
        else:
            if not name:
                name = "card_1"
            newModel.SetProperty("name", newModel.DeduplicateName(name,
                [m.GetProperty("name") for m in self.stackManager.stackModel.childModels]), notify=False)
        return newModel

    def GetDisplayType(self):
        displayTypes = {"card": "Card",
                        "button": "Button",
                        "textfield": "TextField",
                        "textlabel": "TextLabel",
                        "image": "Image",
                        "webview": "WebView",
                        "pen": "Pen",
                        "line": "Line",
                        "rect": "Rectangle",
                        "oval": "Oval",
                        "polygon": "Polygon",
                        "roundrect": "Round Rectangle",
                        "group": "Group",
                        "stack": "Stack"}
        return displayTypes[self.type]

    def SetDirty(self, isDirty):
        if isDirty:
            self.isDirty = True
        else:
            self.isDirty = False
            for child in self.childModels:
                child.SetDirty(False)

    def GetDirty(self):
        if self.isDirty:
            return True
        for card in self.childModels:
            if card.GetDirty():
                return True
        return False

    def CanRotate(self):
        return ("rotation" in self.properties)

    def GetPath(self, subName=None):
        parts = []
        if subName:
            parts.append(subName)
        parts = []
        m = self
        while m.parent:
            parts.append(m.GetProperty("name"))
            m = m.parent
        return ".".join(reversed(parts))

    def SetStackManager(self, stackManager):
        self.stackManager = stackManager
        for m in self.childModels:
            m.SetStackManager(stackManager)

    def GetAffineTransform(self):
        # Get the transform that converts local coords to abs coords
        m = self
        ancestors = []
        aff = wx.AffineMatrix2D()
        while m and m.type not in ["card", "stack"]:
            ancestors.append(m)
            m = m.parent
        for m in reversed(ancestors):
            pos = m.GetProperty("position")
            size = m.GetProperty("size")
            rot = m.GetProperty("rotation")
            aff.Translate(pos[0] + size[0]/2, pos[1] + size[1]/2)
            if rot:
                aff.Rotate(math.radians(-rot))
            aff.Translate(-size[0]/2, -size[1]/2)
        return aff

    def RotatedPoints(self, points, aff=None):
        # convert points in the local system to abs
        if aff is None:
            aff = self.GetAffineTransform()
        return [wx.RealPoint(*aff.TransformPoint(*p)) for p in points]

    def RotatedRectPoints(self, rect, aff=None):
        # Convert local rect to absolute corner points
        points = [rect.TopLeft, rect.TopRight+(1,0), rect.BottomRight+(1,1), rect.BottomLeft+(0,1)]
        return self.RotatedPoints(points, aff)

    def RotatedRect(self, rect, aff=None):
        # Convert local rect to an absolute rect than contains the local one
        points = self.RotatedRectPoints(rect, aff)
        l2 = list(map(list, zip(*points)))
        rotSize = (int(max(l2[0]) - min(l2[0]) - 1), int(max(l2[1]) - min(l2[1]) - 1))
        rotPos_x, rotPos_y = (int(min(l2[0])), int(min(l2[1])))
        return wx.Rect(rotPos_x, rotPos_y, rotSize[0], rotSize[1])

    def UnrotatedRectFromAbsPoints(self, ptA, ptB):
        # Takes 2 absolute points, and creates a local rect
        # This is not fully general purpose: it assumes the parent is a card (not inside a group)
        # This is ok since you can't manually resize a child of a group, and this function is
        # only used from the resize path in the Select Tool.
        rot = self.GetProperty("rotation")
        center = (ptA + ptB)/2
        if rot:
            aff = wx.AffineMatrix2D()
            aff.Translate(*center)
            aff.Rotate(math.radians(rot))
            aff.Translate(*(wx.RealPoint(0,0)-wx.RealPoint(center)))
            ptA = aff.TransformPoint(*ptA)
            ptB = aff.TransformPoint(*ptB)

        bl = wx.Point(int(min(ptA[0], ptB[0])), int(min(ptA[1], ptB[1])))
        tr = wx.Point(int(max(ptA[0], ptB[0])), int(max(ptA[1], ptB[1])))
        return wx.Rect(bl, tr)

    def GetAbsolutePosition(self):
        parent = self.parent
        pos = self.GetProperty("position")
        if self.parent and (self.parent.type != "card" or self.GetProperty("rotation")):
            aff = parent.GetAffineTransform()
            pos = aff.TransformPoint(*pos)
        return wx.RealPoint(*pos)

    def SetAbsolutePosition(self, pos):
        parent = self.parent
        if self.parent and (self.parent.type != "card" or self.GetProperty("rotation")):
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = iaff.TransformPoint(pos[0], pos[1])
        self.SetProperty("position", pos)

    def GetAbsoluteCenter(self):
        s = self.GetProperty("size")
        if self.parent and self.parent.type == "card" and not self.GetProperty("rotation"):
            pos = self.GetProperty("position")
            return pos + tuple(s/2)
        aff = self.GetAffineTransform()
        p = wx.RealPoint(*aff.TransformPoint(int(s[0]/2), int(s[1]/2)))
        return p

    def SetAbsoluteCenter(self, pos):
        parent = self.parent
        s = self.GetProperty("size")
        if not self.parent or self.parent.type == "card":
            self.SetProperty("position", pos - tuple(s/2))
        else:
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = wx.RealPoint(*iaff.TransformPoint(pos[0], pos[1])) - (int(s[0]/2), int(s[1]/2))
            self.SetProperty("position", pos)

    def IsVisible(self):
        """ Returns True iff this object or any of its ancestors has its hidden property set to True """
        if not self.properties["is_visible"]:
            return False
        if self.parent and self.parent.type not in ["card", "stack"]:
            return self.parent.IsVisible()
        return True

    def GetCenter(self):
        return self.GetProperty("center")

    def SetCenter(self, center):
        self.SetProperty("center", center)

    def GetFrame(self):
        p = self.properties["position"]
        s = self.properties["size"]
        return wx.Rect(*[int(x) for x in p], *[int(x) for x in s])

    def GetAbsoluteFrame(self):
        if self.parent and self.parent.type == "card" and not self.GetProperty("rotation"):
            return self.GetFrame()
        return self.RotatedRect(wx.Rect(wx.Point(0,0), self.properties["size"]))

    def SetFrame(self, rect):
        self.SetProperty("position", rect.Position)
        self.SetProperty("size", rect.Size)

    def GetData(self):
        handlers = {}
        for k, v in self.handlers.items():
            if len(v.strip()) > 0:
                handlers[k] = v

        props = self.properties.copy()
        props.pop("is_visible")
        props.pop("speed")
        for k,v in self.propertyTypes.items():
            if v in ["point", "floatpoint", "size"] and k in props:
                props[k] = list(props[k])
            elif v == "dict":
                props[k] = sanitizer.SanitizeDict(props[k], [])

        if len(props["data"]) == 0:
            props.pop("data")

        return {"type": self.type,
                "handlers": handlers,
                "properties": props}

    def SetData(self, data):
        for k, v in data["handlers"].items():
            self.handlers[k] = v
        for k, v in data["properties"].items():
            if k in self.propertyTypes:
                if self.propertyTypes[k] == "point":
                    self.SetProperty(k, wx.Point(tuple(int(x) for x in v)), notify=False)
                elif self.propertyTypes[k] == "floatpoint":
                    self.SetProperty(k, wx.RealPoint(v[0], v[1]), notify=False)
                elif self.propertyTypes[k] == "size":
                    self.SetProperty(k, wx.Size(tuple(int(x) for x in v)), notify=False)
                else:
                    self.SetProperty(k, v, notify=False)

    def SetFromModel(self, model):
        for k, v in model.handlers.items():
            self.handlers[k] = v
        for k, v in model.properties.items():
            if self.propertyTypes[k] == "point":
                self.SetProperty(k, wx.Point(tuple(int(x) for x in v)), notify=False)
            elif self.propertyTypes[k] == "floatpoint":
                self.SetProperty(k, wx.RealPoint(v[0], v[1]), notify=False)
            elif self.propertyTypes[k] == "size":
                self.SetProperty(k, wx.Size(tuple(int(x) for x in v)), notify=False)
            else:
                self.SetProperty(k, v, notify=False)

    # Custom property order and mask for the inspector
    def PropertyKeys(self):
        if self.parent and self.parent.type == 'group':
            keys = self.propertyKeys.copy()
            keys.remove('position')
            keys.remove('size')
            if 'rotation' in keys:
                keys.remove('rotation')
            return keys
        return self.propertyKeys

    # Options currently are string, bool, int, float, point, floatpoint, size, choice, color, file
    def GetPropertyType(self, key):
        return self.propertyTypes.get(key)

    @staticmethod
    def GetPropertyChoices(key):
        if key == "alignment":
            return ["Left", "Center", "Right"]
        elif key == "font":
            return ["Default", "Serif", "Sans-Serif", "Mono"]
        elif key == "fit":
            return ["Center", "Stretch", "Contain", "Fill"]
        elif key == "style":
            return ["Border", "Borderless", "Checkbox", "Radio"]
        elif key == "pen_style":
            return ["Solid", "Long-Dashes", "Dashes", "Dots"]
        return []

    def GetProperty(self, key):
        if key == "center":
            return self.GetAbsoluteCenter()
        elif key in self.properties:
            return self.properties[key]
        return None

    def GetHandler(self, key):
        if key in self.handlers:
            return self.handlers[key]
        return None

    def IsAncestorOf(self, model):
        m = self
        while m.parent:
            if m == model:
                return True
            m = m.parent
        return False

    def GetChildModelByName(self, name):
        if self.properties["name"] == name:
            return self
        for child in self.childModels:
            result = child.GetChildModelByName(name)
            if result:
                return result
        return None

    def GetCard(self):
        if self.type == 'stack':
            return None
        if self.type == "card":
            return self
        if not self.parent:
            return None

        m = self
        while m.parent and m.type != 'card':
            m = m.parent
        return m

    def GetProperties(self):
        return self.properties

    def GetHandlers(self):
        return self.handlers

    def PerformFlips(self, fx, fy, notify=True):
        pass

    def OrderMoveTo(self, index):
        index = index % len(self.parent.childModels) # Convert negative index to positive
        if index < 0 or index > len(self.parent.childModels)-1:
            return
        self.parent.childModels.remove(self)
        self.parent.childModels.insert(index, self)
        if self.GetCard() == self.stackManager.uiCard.model:
            ui = self.stackManager.GetUiViewByModel(self)
            if ui.view:
                self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)
            else:
                ui.parent.uiViews.remove(ui)
                ui.parent.uiViews.insert(index, ui)
                self.stackManager.view.Refresh()

    def OrderMoveBy(self, delta):
        index = self.parent.childModels.index(self) + delta
        self.OrderMoveTo(index)

    def FramePartChanged(self, cdsFramePart):
        if cdsFramePart.role == "position":
            self.SetAbsolutePosition(cdsFramePart)
        elif cdsFramePart.role == "size":
            self.SetProperty("size", cdsFramePart)
        elif cdsFramePart.role == "center":
            self.SetCenter(cdsFramePart)
        elif cdsFramePart.role == "speed":
            self.SetProperty("speed", cdsFramePart)

    def Notify(self, key):
        if self.stackManager:
            self.stackManager.OnPropertyChanged(self, key)

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        if self.stackManager and self.stackManager.isEditing and key in ["speed"]: return
        if key in self.propertyTypes and self.propertyTypes[key] == "point" and not isinstance(value, wx.Point):
            value = wx.Point(tuple(int(x) for x in value))
        elif key in self.propertyTypes and self.propertyTypes[key] == "floatpoint" and not isinstance(value, wx.RealPoint):
            value = wx.RealPoint(value[0], value[1])
        elif key in self.propertyTypes and self.propertyTypes[key] == "size" and not isinstance(value, wx.Point):
            value = wx.Size(tuple(int(x) for x in value))
        elif key in self.propertyTypes and self.propertyTypes[key] == "choice" and value not in self.GetPropertyChoices(key):
            return
        elif key in self.propertyTypes and self.propertyTypes[key] == "color" and isinstance(value, wx.Colour):
            value = value.GetAsString(flags=wx.C2S_HTML_SYNTAX)
        elif key in self.propertyTypes and self.propertyTypes[key] == "uint" and value < 0:
            value = 0

        if key == "name":
            value = re.sub(r'\W+', '', value)
            if not re.match(r'[A-Za-z][A-Za-z_0-9]*', value):
                if notify:
                    self.Notify(key)
                return
        elif key == "size":
            if value.width < self.minSize.width: value.width = self.minSize.width
            if value.height < self.minSize.height: value.height = self.minSize.height
        elif key == "center":
            self.SetAbsoluteCenter(value)
            return
        elif key == "rotation":
            value = value % 360

        if self.properties[key] != value:
            self.properties[key] = value
            if notify:
                self.Notify(key)
            self.isDirty = True

    @staticmethod
    def InterpretPropertyFromString(key, valStr, propType):
        val = valStr
        if propType:
            try:
                if propType == "bool":
                    val = valStr == "True"
                elif propType in ["int", "uint"]:
                    val = int(valStr)
                    if propType == "uint" and val < 0:
                        val = 0
                elif propType == "float":
                    val = float(valStr)
                elif propType in ["point", "floatpoint"]:
                    val = ast.literal_eval(valStr)
                    if not isinstance(val, (list, tuple)) or len(val) != 2 or \
                            not isinstance(val[0], (int, float)) or not isinstance(val[1], (int, float)):
                        raise Exception()
                elif propType == "size":
                    val = ast.literal_eval(valStr)
                    if not isinstance(val, (list, tuple)) or len(val) != 2 or \
                            not isinstance(val[0], (int, float)) or not isinstance(val[1], (int, float)):
                        raise Exception()
                elif propType == "list":
                    if valStr == "":
                        valStr = "[]"
                    val = ast.literal_eval(valStr)
                    if not isinstance(val, (list, tuple)):
                        val = [val]
                elif propType == "dict":
                    if valStr == "":
                        valStr = "{}"
                    val = ast.literal_eval(valStr)
                    if not isinstance(val, dict):
                        val = None
            except:
                return None
        return val

    def SetHandler(self, key, value):
        if self.handlers[key] != value:
            self.handlers[key] = value
            self.isDirty = True

    def SetBounceModels(self, models):
        objs = {}
        for m in models:
            if isinstance(m, ViewModel):
                objs[m] = [None, None]
        self.bounceObjs = objs

    def AddAnimation(self, key, duration, onUpdate, onStart=None, onFinish=None, onCancel=None):
        # On Runner thread
        if self.didSetDown or (self.stackManager and self.stackManager.isEditing): return
        animDict = {"duration": duration if duration != 0 else 0.01,
                    "onStart": onStart,
                    "onUpdate": onUpdate,
                    "onFinish": onFinish,
                    "onCancel": onCancel
                    }
        with self.animLock:
            if key not in self.animations:
                self.animations[key] = [animDict]
                self.StartAnimation(key)
            else:
                self.animations[key].append(animDict)

    def StartAnimation(self, key):
        # On Runner or Main thread
        if key in self.animations:
            animDict = self.animations[key][0]
            if "startTime" not in animDict:
                animDict["startTime"] = time()
                if animDict["onStart"]:
                    animDict["onStart"](animDict)

    def FinishAnimation(self, key):
        # On Main thread
        with self.animLock:
            if key in self.animations:
                animList = self.animations[key]
                animDict = animList[0]
                if len(animList) > 1:
                    del animList[0]
                    self.StartAnimation(key)
                else:
                    del self.animations[key]
                if "startTime" in animDict and animDict["onFinish"]:
                    animDict["onFinish"](animDict)

    def StopAnimation(self, key=None):
        # On Runner thread
        if key:
            if key == "center":
                key = "position"
            # Stop animating this one property
            with self.animLock:
                if key in self.animations:
                    animDict = self.animations[key][0]
                    if "startTime" in animDict and animDict["onCancel"]:
                        animDict["onCancel"](animDict)
                    del self.animations[key]
            return

        # Stop animating all properties
        with self.animLock:
            for (key, animList) in self.animations.items():
                animDict = animList[0]
                if "startTime" in animDict and animDict["onCancel"]:
                    animDict["onCancel"](animDict)
            self.animations = {}

    def DeduplicateName(self, name, existingNames):
        existingNames.extend(self.reservedNames) # disallow globals
        if name in existingNames:
            name = name.rstrip("0123456789_")
            name = self.GetNextAvailableName(name, existingNames)
        return name

    def GetNextAvailableName(self, base, existingNames):
        i = 0
        if base[-1] != "_":
            base += "_"
        while True:
            i += 1
            name = base+str(i)
            if name not in existingNames:
                return name

    def GetProxy(self):
        if not self.proxy:
            self.proxy = self.proxyClass(self)
        return self.proxy

    def RunSetup(self, runner):
        if self.type == "card":
            runner.SetupForCard(self)
        runner.RunHandler(self, "on_setup", None)
        for m in self.childModels:
            m.RunSetup(runner)


class ViewProxy(object):
    """
    This class and its subclasses are the user-accessible objects exposed to event handler code.
    They purposefully contain no attributes for users to avoid, except a single _model reference.
    """

    def __init__(self, model):
        super().__init__()
        self._model = model

    def __repr__(self):
        if self._model:
            return f"<{self._model.GetDisplayType()}:'{self._model.GetProperty('name')}'>"
        return str(self.__class__)

    def __getattr__(self, item):
        model = self._model
        if model:
            for m in model.childModels:
                if m.properties["name"] == item:
                    return m.GetProxy()
        return super().__getattribute__(item)

    def send_message(self, message):
        if not isinstance(message, str):
            raise TypeError("send_message(): message must be a string")

        model = self._model
        if not model: return

        if not model.stackManager.isEditing and model.stackManager.runner and not model.didDelete:
           model.stackManager.runner.RunHandler(model, "on_message", None, message)

    def clone(self, name=None, **kwargs):
        model = self._model
        if not model: return None

        if model.type != "card":
            # update the model immediately on the runner thread
            newModel = model.CreateCopy(name)
            newModel.SetProperty("speed", model.GetProperty("speed"), notify=False)
            newModel.lastOnPeriodicTime = time()
            if not self.is_visible:
                newModel.SetProperty("is_visible", False, notify=False)
            for k,v in kwargs.items():
                if hasattr(newModel.GetProxy(), k):
                    setattr(newModel.GetProxy(), k, v)
                else:
                    raise TypeError(f"clone(): unable to set property {k}")

            self._model.stackManager.uiCard.model.AddChild(newModel)
            newModel.RunSetup(model.stackManager.runner)
            if newModel.GetCard() != model.stackManager.uiCard.model:
                model.stackManager.runner.SetupForCard(model.stackManager.uiCard.model)

            @RunOnMainAsync
            def func():
                if not newModel.didSetDown:
                    # add the view on the main thread
                    newModel.stackManager.AddUiViewsFromModels([newModel], False)
            func()
        else:
            @RunOnMainSync
            def func():
                # When cloning a card, update the model and view together in a rare synchronous call to the main thread
                newModel = model.stackManager.DuplicateCard(model)

                if "center" in kwargs and "size" in kwargs:
                    newModel.SetProperty("size", kwargs["size"])
                    newModel.SetProperty("center", kwargs["center"])
                    kwargs.pop("size")
                    kwargs.pop("center")

                for k,v in kwargs.items():
                    if hasattr(newModel.GetProxy(), k):
                        setattr(newModel.GetProxy(), k, v)
                    else:
                        raise TypeError(f"clone(): unable to set property {k}")

                return newModel
            newModel = func()

        return newModel.GetProxy()

    def delete(self):
        model = self._model
        if not model or not model.parent or model.parent.type == "group" or model.didDelete:
            return

        model.didDelete = True
        # immediately update the model
        sm = model.stackManager
        if model.type != "card":
            model.parent.RemoveChild(model)

        if model.type != "card":
            @RunOnMainAsync
            def func():
                # update views on the main thread
                sm.RemoveUiViewByModel(model)
            func()
        else:
            @RunOnMainSync
            def func():
                # When cloning a card, update the model and view together in a rare synchronous call to the main thread
                sm.RemoveCardRaw(model)
            func()

    @property
    def name(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("name")

    @property
    def type(self):
        model = self._model
        if not model: return None
        return model.type

    @property
    def data(self):
        model = self._model
        if not model: return {}
        return model.GetProperty("data")

    @property
    def parent(self):
        model = self._model
        if not model: return None
        parent = model.parent
        if parent: parent = parent.GetProxy()
        return parent

    @property
    def children(self):
        model = self._model
        if not model: return []
        return [m.GetProxy() for m in model.childModels]

    def child_with_base_name(self, base):
        model = self._model
        if model and model.childModels:
            for m in model.childModels:
                if m.properties["name"].startswith(base):
                    return m.GetProxy()
        return None

    @property
    def size(self):
        model = self._model
        if not model: return wx.Size(0,0)
        return CDSSize(model.GetProperty("size"), model=model, role="size")
    @size.setter
    def size(self, val):
        try:
            val = wx.Size(val[0], val[1])
        except:
            raise ValueError("size must be a size or a list of two numbers")
        model = self._model
        if not model: return
        model.SetProperty("size", val)

    @property
    def position(self):
        model = self._model
        if not model: return wx.RealPoint(0,0)
        return CDSRealPoint(model.GetAbsolutePosition(), model=model, role="position")
    @position.setter
    def position(self, val):
        try:
            val = wx.RealPoint(val[0], val[1])
        except:
            raise ValueError("position must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetAbsolutePosition(val)

    @property
    def speed(self):
        model = self._model
        if not model: return wx.RealPoint(0,0)
        speed = CDSPoint(model.GetProperty("speed"), model=model, role="speed")
        return speed
    @speed.setter
    def speed(self, val):
        try:
            val = wx.Point(int(val[0]), int(val[1]))
        except:
            raise ValueError("speed must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetProperty("speed", val)

    @property
    def center(self):
        model = self._model
        if not model: return wx.RealPoint(0,0)
        return CDSRealPoint(model.GetCenter(), model=model, role="center")
    @center.setter
    def center(self, center):
        try:
            center = wx.RealPoint(center[0], center[1])
        except:
            raise ValueError("center must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetCenter(center)

    @RunOnMainAsync
    def flip_horizontal(self):
        model = self._model
        if not model: return
        model.PerformFlips(True, False)

    @RunOnMainAsync
    def flip_vertical(self):
        model = self._model
        if not model: return
        model.PerformFlips(False, True)

    @RunOnMainSync
    def order_to_front(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(-1)

    @RunOnMainSync
    def order_forward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(1)

    @RunOnMainSync
    def order_backward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(-1)

    @RunOnMainSync
    def order_to_back(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(0)

    def order_to_index(self, i):
        if not isinstance(i, int):
            raise TypeError("order_to_index(): index must be a number")

        model = self._model
        if not model: return

        if i < 0 or i >= len(model.parent.childModels):
            raise TypeError("order_to_index(): index is out of bounds")

        @RunOnMainSync
        def f():
            if model.didSetDown: return
            model.OrderMoveTo(i)
        f()

    def show(self):
        self.is_visible = True
    def hide(self):
        self.is_visible = False

    @property
    def is_visible(self):
        model = self._model
        if not model: return False
        return model.IsVisible()
    @is_visible.setter
    def is_visible(self, val):
        model = self._model
        if not model: return
        model.SetProperty("is_visible", bool(val))

    @property
    def rotation(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("rotation")
    @rotation.setter
    def rotation(self, val):
        if self._model.GetProperty("rotation") is None:
            raise TypeError("object does not support rotation")
        if not isinstance(val, (int, float)):
            raise TypeError("rotation must be a number")
        model = self._model
        if not model: return
        model.SetProperty("rotation", val)

    def get_code_for_event(self, eventName):
        model = self._model
        if not model: return ""
        return model.handlers[eventName]

    def set_code_for_event(self, eventName, code):
        model = self._model
        if not model: return
        if not isinstance(eventName, str):
            raise TypeError("set_code_for_event(): eventName must be a string")
        if not isinstance(code, str):
            raise TypeError("set_code_for_event(): code must be a string")
        if eventName not in model.handlers:
            raise TypeError(f"set_code_for_event(): this object has no event called '{eventName}'")

        model.handlers[eventName] = code
        model.stackManager.runner.HandlerChanged(model, eventName)

    def set_bounce_objects(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError("set_bounce_objects(): objects needs to be a list of cardstock objects")
        models = [o._model for o in objects if isinstance(o, ViewProxy)]
        self._model.SetBounceModels(models)

    def stop_handling_mouse_event(self):
        self._model.stackManager.runner.stop_handling_mouse_event()

    def is_touching_point(self, point):
        if not isinstance(point, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
            raise TypeError("is_touching_point(): point needs to be a point or a list of two numbers")
        if len(point) != 2:
            raise TypeError("is_touching_point(): point needs to be a point or a list of two numbers")
        try:
            int(point[0]), int(point[1])
        except:
            raise ValueError("is_touching_point(): point needs to be a point or a list of two numbers")

        model = self._model
        if not model: return False

        @RunOnMainSync
        def f():
            if model.didSetDown: return False
            s = model.stackManager.GetUiViewByModel(model)
            if not s:
                return False
            sreg = s.GetHitRegion()
            return sreg.Contains(wx.Point(tuple(int(x) for x in point))) == wx.InRegion
        return f()

    def is_touching(self, obj):
        if not isinstance(obj, ViewProxy):
            raise TypeError("is_touching(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel: return False

        @RunOnMainSync
        def f():
            if model.didSetDown: return False
            s = model.stackManager.GetUiViewByModel(model)
            o = model.stackManager.GetUiViewByModel(oModel)
            if not s or not o:
                return False
            sreg = wx.Region(s.GetHitRegion())
            oreg = o.GetHitRegion()
            sreg.Intersect(oreg)
            return not sreg.IsEmpty()
        return f()

    def is_touching_edge(self, obj, skipIsTouchingCheck=False):
        if not isinstance(obj, ViewProxy):
            raise TypeError("is_touching_edge(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel: return []
        ui = model.stackManager.GetUiViewByModel(model)
        oUi = model.stackManager.GetUiViewByModel(oModel)

        @RunOnMainSync
        def f():
            if model.didSetDown or oModel.didSetDown: return []

            if not skipIsTouchingCheck and not self.is_touching(obj):
                return []

            def intersectTest(r, edge):
                testReg = wx.Region(r)
                testReg.Intersect(edge)
                return not testReg.IsEmpty()

            reg = ui.GetHitRegion()
            oRot = oModel.GetProperty("rotation")
            if oRot is None: oRot = 0

            rect = oModel.GetFrame() # other frame in card coords
            cornerSetback = 4
            # Pull edge lines away from the corners, so we don't always hit a corner when 2 objects touch
            rects = [wx.Rect(rect.TopLeft+(cornerSetback,0), rect.TopRight+(-cornerSetback,1)),
                      wx.Rect(rect.TopRight+(-1,cornerSetback), rect.BottomRight+(0,-cornerSetback)),
                      wx.Rect(rect.BottomLeft+(cornerSetback,-1), rect.BottomRight+(-cornerSetback,0)),
                      wx.Rect(rect.TopLeft+(0,cornerSetback), rect.BottomLeft+(1,-cornerSetback))]

            if oRot == 0:
                bottom = rects[0]
                right = rects[1]
                top = rects[2]
                left = rects[3]
            else:
                for r in rects:
                    r.Offset(wx.Point(0,0)-rect.TopLeft)
                bottom = oUi.MakeRegionFromLocalRect(rects[0])
                right = oUi.MakeRegionFromLocalRect(rects[1])
                top = oUi.MakeRegionFromLocalRect(rects[2])
                left = oUi.MakeRegionFromLocalRect(rects[3])

            def RotEdge(rot):
                # Rotate reported edge hits according to other object's rotation
                edgesMap = [["Top"], ["Top", "Right"], ["Right"], ["Bottom", "Right"],
                            ["Bottom"], ["Bottom", "Left"], ["Left"], ["Top", "Left"]]
                i = int(((rot+22.5)%360)/45)
                return edgesMap[i]

            edges = set()
            if intersectTest(reg, top): [edges.add(e) for e in RotEdge(oRot)]
            if intersectTest(reg, bottom): [edges.add(e) for e in RotEdge(oRot+180)]
            if intersectTest(reg, left): [edges.add(e) for e in RotEdge(oRot+270)]
            if intersectTest(reg, right): [edges.add(e) for e in RotEdge(oRot+90)]
            if len(edges) == 3 and "Top" in edges and "Bottom" in edges:
                edges.remove("Top")
                edges.remove("Bottom")
            if len(edges) == 3 and "Left" in edges and "Right" in edges:
                edges.remove("Left")
                edges.remove("Right")
            return edges
        return f()

    def animate_position(self, duration, end_position, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_position(): duration must be a number")
        try:
            end_position = wx.RealPoint(*end_position)
        except:
            raise ValueError("animate_position(): end_position must be a point or a list of two numbers")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_position(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        def onStart(animDict):
            origPosition = model.GetAbsolutePosition()
            offsetPt = end_position - tuple(origPosition)
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origPosition"] = origPosition
            animDict["offset"] = offset
            model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetAbsolutePosition(animDict["origPosition"] + tuple(animDict["offset"] * ease(progress, easing)))

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def animate_center(self, duration, end_center, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_center(): duration must be a number")
        try:
            end_center = wx.RealPoint(*end_center)
        except:
            raise ValueError("animate_center(): end_center must be a point or a list of two numbers")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_center(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        def onStart(animDict):
            origCenter = model.GetCenter()
            offsetPt = end_center - tuple(origCenter)
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origCenter"] = origCenter
            animDict["offset"] = offset
            self._model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetCenter(animDict["origCenter"] + tuple(animDict["offset"] * ease(progress, easing)))

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def animate_size(self, duration, end_size, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_size(): duration must be a number")
        try:
            end_size = wx.Size(end_size)
        except:
            raise ValueError("animate_size(): end_size must be a size or a list of two numbers")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_size(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        def onStart(animDict):
            origSize = model.GetProperty("size")
            offset = wx.Size(end_size-tuple(origSize))
            animDict["origSize"] = origSize
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("size", animDict["origSize"] + tuple(animDict["offset"] * ease(progress, easing)))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        model.AddAnimation("size", duration, onUpdate, onStart, internalOnFinished)

    def animate_rotation(self, duration, end_rotation, force_direction=0, easing=None, on_finished=None):
        if self._model.GetProperty("rotation") is None:
            raise TypeError("animate_rotation(): object does not support rotation")

        if not isinstance(duration, (int, float)):
            raise TypeError("animate_rotation(): duration must be a number")
        if not isinstance(end_rotation, (int, float)):
            raise TypeError("animate_rotation(): end_rotation must be a number")
        if not isinstance(force_direction, (int, float)):
            raise TypeError("animate_rotation(): force_direction must be a number")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_rotation(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        end_rotation = end_rotation

        def onStart(animDict):
            origVal = self.rotation
            animDict["origVal"] = origVal
            offset = end_rotation - origVal
            if force_direction:
                if force_direction > 0:
                    if offset <= 0: offset += 360
                elif force_direction < 0:
                    if offset >= 0: offset -= 360
            else:
                if offset > 180: offset -= 360
                if offset < -180: offset += 360
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("rotation", (animDict["origVal"] + animDict["offset"] * ease(progress, easing))%360)

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        model.AddAnimation("rotation", duration, onUpdate, onStart, internalOnFinished)

    def stop_animating(self, property_name=None):
        model = self._model
        if not model: return
        model.StopAnimation(property_name)
