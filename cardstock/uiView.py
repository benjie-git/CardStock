import threading

import wx
import threading
import ast
import re
import generator
import helpData
from time import time
from codeRunnerThread import RunOnMainSync, RunOnMainAsync
from cardstockFrameParts import *
import sanitizer
import math
import flippedGCDC


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

            mSize = self.model.GetProperty("size")
            if mSize[0] > 0 and mSize[1] > 0:
                self.view.SetRect(self.stackManager.ConvRect(self.model.GetAbsoluteFrame()))

            self.BindEvents(view)
            view.Bind(wx.EVT_SIZE, self.OnResize)
            self.view.Show(not self.model.IsHidden())

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
                self.view.SetRect(self.stackManager.ConvRect(self.model.GetAbsoluteFrame()))
                self.view.Refresh()
            self.ClearHitRegion()
            self.stackManager.view.Refresh()
        elif key == "hidden":
            if self.view:
                self.view.Show(not self.model.IsHidden())
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
        if self.stackManager.runner and self.model.GetHandler("OnMouseDown"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseDown", event)
        event.Skip()

    def OnMouseMove(self, event):
        self.hasMouseMoved = True
        event.Skip()

    def OnMouseUpOutside(self, event):
        pass

    def OnMouseUp(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnMouseUp"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseUp", event)
        event.Skip()

    def OnMouseEnter(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnMouseEnter"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseEnter", event)
        event.Skip()

    def OnMouseExit(self, event):
        self.hasMouseMoved = False
        if self.stackManager and self.stackManager.runner and self.model.GetHandler("OnMouseExit"):
            self.stackManager.runner.RunHandler(self.model, "OnMouseExit", event)
        event.Skip()

    def RunAnimations(self, onFinishedCalls, elapsedTime):
        # Move the object by speed.x and speed.y pixels per second
        updateList = []
        finishList = []
        with self.model.animLock:
            if self.model.type not in ["stack", "card"]:
                speed = self.model.GetProperty("speed")
                if speed != (0,0) and "position" not in self.model.animations:
                    pos = self.model.GetProperty("position")
                    self.model.SetProperty("position", [pos.x + speed.x*elapsedTime, pos.y + speed.y*elapsedTime])

            # Run any in-progress animations
            now = time()
            for (key, animList) in self.model.animations.copy().items():
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
        for key in finishList:
            def deferFinish():
                self.model.FinishAnimation(key)
            onFinishedCalls.append(deferFinish)

    def FindCollisions(self, collisions):
        # Find collisions between this object and others in its bounceObjs list
        # and add them to the collisions list, to be handled after all are found.
        removeFromBounceObjs = []
        if not self.model.didSetDown and not self.model.GetProperty("hidden") and tuple(self.model.GetProperty("speed")) != (0, 0):
            for k,v in self.model.bounceObjs.items():
                other_ui = self.stackManager.GetUiViewByModel(k)
                (mode, last_dist) = v

                if other_ui.model.GetProperty("hidden"):
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
                    self.model.bounceObjs[k][0] = "In" if other_ui.model.GetProxy().IsTouchingPoint(self.model.GetCenter()) else "Out"
                    self.model.bounceObjs[k][1] = new_dist
                    continue

                edges = self.model.GetProxy().IsTouchingEdge(other_ui.model.GetProxy(), mode == "In")
                if mode == "In" and not edges:
                    if not other_ui.model.GetProxy().IsTouchingPoint(self.model.GetCenter()):
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
                            collisions[key] = (self, other_ui, selfBounceAxes, otherBounceAxes, edges)

                self.model.bounceObjs[k][1] = new_dist

            for k in removeFromBounceObjs:
                del self.model.bounceObjs[k]

    def PerformBounce(self, info):
        # Perform this bounce for this object, and the other object
        (this_ui, other_ui, selfAxes, otherAxes, edges) = info
        ss = self.model.GetProxy().speed
        os = other_ui.model.GetProxy().speed
        sc = self.model.GetProxy().center
        oc = other_ui.model.GetProxy().center

        # Flags
        selfBounce = other_ui.model in self.model.bounceObjs
        selfBounceInside = False if not selfBounce else self.model.bounceObjs[other_ui.model][0] == "In"
        otherBounce = self.model in other_ui.model.bounceObjs

        # Determine how far these two objects have overlapped, and fix by
        # moving this object back out, in the shorter direction
        (dx, dy) = (0, 0)
        if "H" in selfAxes:
            sf = self.model.GetAbsoluteFrame()
            of = other_ui.model.GetAbsoluteFrame()
            if selfBounceInside:
                if ss[0] > 0 and sf.Right > of.Right:
                    dx = sf.Right - of.Right
                elif ss[0] < 0 and sf.Left < of.Left:
                    dx = sf.Left - of.Left
            else:
                if ss[0] > 0 and sf.Right > of.Left:
                    dx = sf.Right - of.Left
                elif ss[0] < 0 and sf.Left < of.Right:
                    dx = sf.Left - of.Right
        if "V" in selfAxes:
            sf = self.model.GetAbsoluteFrame()
            of = other_ui.model.GetAbsoluteFrame()
            if selfBounceInside:
                if ss[1] > 0 and sf.Bottom > of.Bottom:
                    dy = sf.Bottom - of.Bottom
                elif ss[1] < 0 and sf.Top < of.Top:
                    dy = sf.Top - of.Top
            else:
                if ss[1] > 0 and sf.Bottom > of.Top:
                    dy = sf.Bottom - of.Top
                elif ss[1] < 0 and sf.Top < of.Bottom:
                    dy = sf.Top - of.Bottom
        if not selfBounceInside and dx != 0 and dy != 0:
            if abs(dx) > abs(dy):
                dx = 0
            else:
                dy = 0
        sc.x -= dx
        sc.y -= dy

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
                if self.stackManager.runner and self.model.GetHandler("OnBounce"):
                    self.stackManager.runner.RunHandler(self.model, "OnBounce", None,
                                                        [other_ui.model.GetProxy(), edge])

        if self.model in other_ui.model.bounceObjs:
            # Use this opposites dict to show the right edge names in the other object's OnBounce calls
            opposites = {"Top": "Bottom", "Bottom": "Top", "Left": "Right", "Right": "Left"}
            for edge in edges:
                otherEdge = edge if selfBounceInside else opposites[edge] # Don't flip names for inside bounces
                if self.stackManager.runner and other_ui.model.GetHandler("OnBounce"):
                    self.stackManager.runner.RunHandler(other_ui.model, "OnBounce", None,
                                                        [self.model.GetProxy(), otherEdge])

    def OnPeriodic(self, event):
        didRun = False
        if self.hasMouseMoved:
            self.hasMouseMoved = False
            if self.stackManager.runner and self.model.GetHandler("OnMouseMove"):
                self.stackManager.runner.RunHandler(self.model, "OnMouseMove", event)
                didRun = True

        if self.stackManager.runner and self.model.GetHandler("OnPeriodic"):
            self.stackManager.runner.RunHandler(self.model, "OnPeriodic", event)
            didRun = True

        return didRun

    def DoPaint(self, gc):
        self.PrePaint(gc)
        if not self.model.IsHidden():
            self.Paint(gc)
        for ui in self.uiViews:
            ui.DoPaint(gc)
        self.PostPaint(gc)

    def DoPaintSelectionBoxes(self, gc):
        self.PrePaint(gc)
        if self.isSelected:
            self.PaintSelectionBox(gc)
        for ui in self.uiViews:
            ui.DoPaintSelectionBoxes(gc)
        self.PostPaint(gc)

    def PrePaint(self, gc):
        # Rotate and Translate the GC, such that we can draw in local coords
        stackSize = self.stackManager.stackModel.GetProperty("size")
        pos = self.model.GetProperty("position")
        cen = self.model.GetProperty("size")/2
        rot = self.model.GetProperty("rotation")
        rot = math.radians(rot) if rot else None
        gc.GetGraphicsContext().PushState()

        gc.GetGraphicsContext().Translate(pos[0]+cen[0], stackSize.height-(pos[1]+cen[1]))
        if rot:
            gc.GetGraphicsContext().Rotate(rot)
        gc.GetGraphicsContext().Translate(-cen[0], cen[1]-stackSize.height)

    def Paint(self, gc):
        self.PaintBoundingBox(gc)

    def PaintBoundingBox(self, gc, color='Gray'):
        if self.stackManager.isEditing:
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(color, 1, wx.PENSTYLE_DOT))

            pos = wx.Point(0,0)-list(self.model.GetProperty("position"))
            f = self.model.GetFrame()
            f.Offset(pos)
            gc.DrawRectangle(f)

    def PaintSelectionBox(self, gc):
        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            pos = wx.Point(0,0)-list(self.model.GetProperty("position"))
            f = self.model.GetFrame()
            f.Offset(pos)

            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Inflate(2))

            if self.model.parent and self.model.parent.type != "group":
                gc.SetPen(wx.TRANSPARENT_PEN)
                gc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_SOLID))
                for box in self.GetLocalResizeBoxRects().values():
                    gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def PostPaint(self, gc):
        gc.GetGraphicsContext().PopState()

    def HitTest(self, pt):
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
        return {k:wx.Point(aff.TransformPoint(*p)) for k,p in points.items()}

    def GetResizeBoxRects(self):
        points = self.GetResizeBoxPoints()
        return {k:wx.Rect(p.x-6, p.y-6, 12, 12) for k,p in points.items()}

    def GetLocalResizeBoxRects(self):
        points = self.GetLocalResizeBoxPoints()
        return {k:wx.Rect(p.x-6, p.y-6, 12, 12) for k,p in points.items()}

    def ClearHitRegion(self):
        self.hitRegion = None
        if self.parent and self.parent.model.type == "group":
            self.parent.ClearHitRegion()

    def GetHitRegion(self):
        if not self.hitRegion:
            self.MakeHitRegion()
        return self.hitRegion

    def MakeHitRegion(self):
        # Make a region in absolute/card coordinates
        if self.model.IsHidden():
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
        regOffset = 10

        height = rotSize[1]+2*regOffset
        bmp = wx.Bitmap(width=rotSize[0]+2*regOffset, height=height, depth=1)
        gc = flippedGCDC.FlippedMemoryDC(bmp, self.stackManager, height)
        gc.SetBackground(wx.Brush('black', wx.BRUSHSTYLE_SOLID))
        gc.SetBrush(wx.Brush('white', wx.BRUSHSTYLE_SOLID))
        gc.Clear()

        aff = self.model.GetAffineTransform()
        vals = aff.Get()
        # Draw into region bmp rotated but not translated
        vals = (vals[0].m_11, vals[0].m_12, vals[0].m_21, vals[0].m_22, vals[1][0] - (rotPos_x-regOffset), vals[1][1] - (rotPos_y-regOffset))
        aff = gc.GetGraphicsContext().CreateMatrix(*vals)

        path = gc.GetGraphicsContext().CreatePath()
        p1 = rect.TopLeft
        p2 = rect.BottomRight
        path.AddRectangle(p1[0], min(p1[1], p2[1]), p2[0] - p1[0], abs(p2[1] - p1[1]))
        path.Transform(aff)
        gc.GetGraphicsContext().FillPath(path)

        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            path = gc.GetGraphicsContext().CreatePath()
            for resizerRect in self.GetLocalResizeBoxRects().values():
                path.AddRectangle(resizerRect.Left, resizerRect.Top, resizerRect.Width, resizerRect.Height)
            path.Transform(aff)
            gc.GetGraphicsContext().FillPath(path)
            gc.GetGraphicsContext().Flush()

        reg = bmp.ConvertToImage().ConvertToRegion(0,0,0)
        reg.Offset(rotPos_x-regOffset, rotPos_y-regOffset)
        self.hitRegion = reg

    handlerDisplayNames = {
        'OnSetup':      "OnSetup():",
        'OnShowCard':   "OnShowCard():",
        'OnHideCard':   "OnHideCard():",
        'OnClick':      "OnClick():",
        'OnTextEnter':  "OnTextEnter():",
        'OnTextChanged':"OnTextChanged():",
        'OnMouseDown':  "OnMouseDown(mousePos):",
        'OnMouseMove':  "OnMouseMove(mousePos):",
        'OnMouseUp':    "OnMouseUp(mousePos):",
        'OnMouseEnter': "OnMouseEnter(mousePos):",
        'OnMouseExit':  "OnMouseExit(mousePos):",
        'OnDoneLoading':"OnDoneLoading(url, didLoad):",
        'OnBounce':     "OnBounce(otherObject, edge)",
        'OnMessage':    "OnMessage(message):",
        'OnKeyDown':    "OnKeyDown(keyName):",
        'OnKeyHold':    "OnKeyHold(keyName, elapsedTime):",
        'OnKeyUp':      "OnKeyUp(keyName):",
        'OnResize':     "OnResize():",
        'OnPeriodic':   "OnPeriodic(elapsedTime):",
        'OnExitStack':  "OnExitStack():",
    }


class ViewModel(object):
    """
    This is the abstract base class for the other model classes.
    The model holds the property values and event handler text for each object.
    It also holds the type of each property, and the ordered list of properties to display in the inspector.
    It also handles animating properties of the object, like position, size, or color.
    """

    minSize = wx.Size(20, 20)
    reservedNames = helpData.HelpData.ReservedNames()

    def __init__(self, stackManager):
        super().__init__()
        self.type = None
        self.parent = None
        self.handlers = {"OnSetup": "",
                         "OnMouseEnter": "",
                         "OnMouseDown": "",
                         "OnMouseMove": "",
                         "OnMouseUp": "",
                         "OnMouseExit": "",
                         "OnBounce": "",
                         "OnMessage": "",
                         "OnPeriodic": ""
                         }
        self.initialEditHandler = "OnMouseDown"

        self.properties = {"name": "",
                           "size": wx.Size(0,0),
                           "position": wx.RealPoint(0,0),
                           "speed": wx.Point(0,0),
                           "hidden": False,
                           "data": {}
                           }
        self.propertyKeys = ["name", "position", "size"]
        self.propertyTypes = {"name": "string",
                              "position": "floatpoint",
                              "center": "floatpoint",
                              "size": "size",
                              "speed": "point",
                              "hidden": "bool",
                              "data": "dict"
                              }
        self.propertyChoices = {}

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

    def __repr__(self):
        return "<"+str(self.__class__.__name__) + ":" + self.type + ":'" + self.GetProperty("name")+"'>"

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

    def CreateCopy(self):
        data = self.GetData()
        newModel = generator.StackGenerator.ModelFromData(self.stackManager, data)
        if newModel.type != "card":
            self.stackManager.uiCard.model.DeduplicateNamesForModels([newModel])
        else:
            newModel.SetProperty("name", newModel.DeduplicateName("card_1",
                [m.GetProperty("name") for m in self.stackManager.stackModel.childModels]), notify=False)
        return newModel

    def GetType(self):
        return self.type

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
                        "poly": "Polygon",
                        "roundrect": "Round Rectangle",
                        "group": "Group"}
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

    def GetPath(self):
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
            aff.Translate(*(pos + (int(size[0]/2), int(size[1]/2))))
            if rot:
                aff.Rotate(math.radians(-rot))
            aff.Translate(-int(size[0]/2), -int(size[1]/2))
        return aff

    def RotatedPoints(self, points):
        aff = self.GetAffineTransform()
        return [wx.Point(aff.TransformPoint(*p)) for p in points]

    def RotatedRectPoints(self, rect):
        points = [rect.TopLeft, rect.TopRight+(1,0), rect.BottomRight+(1,1), rect.BottomLeft+(0,1)]
        return self.RotatedPoints(points)

    def RotatedRect(self, rect):
        points = self.RotatedRectPoints(rect)
        l2 = list(map(list, zip(*points)))
        rotSize = (max(l2[0]) - min(l2[0]) - 1, max(l2[1]) - min(l2[1]) - 1)
        rotPos_x, rotPos_y = (min(l2[0]), min(l2[1]))
        return wx.Rect(rotPos_x, rotPos_y, rotSize[0], rotSize[1])

    def UnrotatedRectFromAbsPoints(self, ptA, ptB):
        rot = self.GetProperty("rotation")
        center = (ptA + ptB)/2
        aff = wx.AffineMatrix2D()
        aff.Translate(*center)
        if rot:
            aff.Rotate(math.radians(rot))
        aff.Translate(*(wx.Point(0,0)-center))

        ptA = aff.TransformPoint(*ptA)
        ptB = aff.TransformPoint(*ptB)
        bl = wx.Point(min(ptA[0], ptB[0]), min(ptA[1], ptB[1]))
        tr = wx.Point(max(ptA[0], ptB[0]), max(ptA[1], ptB[1]))
        return wx.Rect(bl, tr)

    def GetAbsolutePosition(self):
        parent = self.parent
        pos = self.GetProperty("position")
        if parent:
            aff = parent.GetAffineTransform()
            pos = aff.TransformPoint(*pos)
        return wx.RealPoint(pos)

    def SetAbsolutePosition(self, pos):
        parent = self.parent
        if parent:
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = iaff.TransformPoint(pos[0], pos[1])
        self.SetProperty("position", pos)

    def GetAbsoluteCenter(self):
        s = self.GetProperty("size")
        aff = self.GetAffineTransform()
        p = wx.Point(*aff.TransformPoint(int(s[0]/2), int(s[1]/2)))
        return p

    def SetAbsoluteCenter(self, pos):
        parent = self.parent
        if parent:
            s = self.GetProperty("size")
            iaff = parent.GetAffineTransform()
            iaff.Invert()
            pos = wx.RealPoint(*iaff.TransformPoint(pos[0], pos[1])) - (int(s[0]/2), int(s[1]/2))
        self.SetProperty("position", pos)

    def IsHidden(self):
        """ Returns True iff this object or any of its ancestors has its hidden property set to True """
        if self.properties["hidden"]:
            return True
        if self.parent:
            return self.parent.IsHidden()
        return False

    def GetCenter(self):
        return self.GetProperty("center")

    def SetCenter(self, center):
        self.SetProperty("center", center)

    def GetFrame(self):
        p = wx.Point(self.GetProperty("position"))
        s = self.GetProperty("size")
        return wx.Rect(p, s)

    def GetAbsoluteFrame(self):
        return self.RotatedRect(wx.Rect(wx.Point(0,0), self.GetProperty("size")))

    def SetFrame(self, rect):
        self.SetProperty("position", rect.Position)
        self.SetProperty("size", rect.Size)

    def GetData(self):
        handlers = {}
        for k, v in self.handlers.items():
            if len(v.strip()) > 0:
                handlers[k] = v

        props = self.properties.copy()
        props.pop("hidden")
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
                    self.SetProperty(k, wx.Point(v), notify=False)
                elif self.propertyTypes[k] == "floatpoint":
                    self.SetProperty(k, wx.RealPoint(v[0], v[1]), notify=False)
                elif self.propertyTypes[k] == "size":
                    self.SetProperty(k, wx.Size(v), notify=False)
                else:
                    self.SetProperty(k, v, notify=False)

    def SetFromModel(self, model):
        for k, v in model.handlers.items():
            self.handlers[k] = v
        for k, v in model.properties.items():
            if self.propertyTypes[k] == "point":
                self.SetProperty(k, wx.Point(v), notify=False)
            elif self.propertyTypes[k] == "floatpoint":
                self.SetProperty(k, wx.RealPoint(v[0], v[1]), notify=False)
            elif self.propertyTypes[k] == "size":
                self.SetProperty(k, wx.Size(v), notify=False)
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
        return self.propertyTypes[key]

    def GetPropertyChoices(self, key):
        return self.propertyChoices[key]

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
        if key in self.propertyTypes and self.propertyTypes[key] == "point" and not isinstance(value, wx.Point):
            value = wx.Point(value)
        elif key in self.propertyTypes and self.propertyTypes[key] == "floatpoint" and not isinstance(value, wx.RealPoint):
            value = wx.RealPoint(value[0], value[1])
        elif key in self.propertyTypes and self.propertyTypes[key] == "size" and not isinstance(value, wx.Point):
            value = wx.Size(value)
        elif key in self.propertyTypes and self.propertyTypes[key] == "choice" and value not in self.propertyChoices[key]:
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

    def InterpretPropertyFromString(self, key, valStr):
        propType = self.propertyTypes[key]
        val = valStr
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
                if not isinstance(val, (list, tuple)) or len(val) != 2:
                    raise Exception()
            elif propType == "size":
                val = ast.literal_eval(valStr)
                if not isinstance(val, (list, tuple)) or len(val) != 2:
                    raise Exception()
            elif propType == "list":
                if valStr == "":
                    valStr = "[]"
                val = ast.literal_eval(valStr)
                if not isinstance(val, (list, tuple)):
                    raise Exception()
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
        if self.didSetDown: return
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
        if self.GetHandler("OnSetup"):
            runner.RunHandler(self, "OnSetup", None)
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

    def __getattr__(self, item):
        model = self._model
        if model:
            for m in model.childModels:
                if m.properties["name"] == item:
                    return m.GetProxy()
        return super().__getattribute__(item)

    def SendMessage(self, message):
        if not isinstance(message, str):
            raise TypeError("SendMessage(): message must be a string")

        model = self._model
        if not model: return

        if model.stackManager.runner:
           model.stackManager.runner.RunHandler(model, "OnMessage", None, message)

    def Focus(self):
        model = self._model
        if not model: return

        if model.stackManager.runner:
            model.stackManager.runner.SetFocus(self)

    @property
    @RunOnMainSync
    def hasFocus(self):
        model = self._model
        if not model: return False

        uiView = model.stackManager.GetUiViewByModel(model)
        if uiView and uiView.view:
            return uiView.view.HasFocus()

    def Clone(self, **kwargs):
        model = self._model
        if not model: return None

        if model.type != "card":
            # update the model immediately on the runner thread
            newModel = model.CreateCopy()
            newModel.SetProperty("speed", model.GetProperty("speed"), notify=False)
            newModel.lastOnPeriodicTime = time()
            if not self.visible:
                newModel.SetProperty("hidden", True, notify=False)
            for k,v in kwargs.items():
                if hasattr(newModel.GetProxy(), k):
                    setattr(newModel.GetProxy(), k, v)
                else:
                    raise TypeError(f"Clone(): unable to set property {k}")

            model.GetCard().AddChild(newModel)
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
                newModel = model.stackManager.DuplicateCard()

                if "center" in kwargs and "size" in kwargs:
                    newModel.SetProperty("size", kwargs["size"])
                    newModel.SetProperty("center", kwargs["center"])
                    kwargs.pop("size")
                    kwargs.pop("center")

                for k,v in kwargs.items():
                    if hasattr(newModel.GetProxy(), k):
                        setattr(newModel.GetProxy(), k, v)
                    else:
                        raise TypeError(f"Clone(): unable to set property {k}")

                return newModel
            newModel = func()

        return newModel.GetProxy()

    def Delete(self):
        model = self._model
        if not model or not model.parent or model.parent.type == "group":
            return

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

    @RunOnMainSync
    def Cut(self):
        # update the model and view together in a rare synchronous call to the main thread
        model = self._model
        if not model: return

        model.stackManager.CutModels([model], False)

    @RunOnMainSync
    def Copy(self):
        # update the model and view together in a rare synchronous call to the main thread
        model = self._model
        if not model: return

        model.stackManager.CopyModels([model])

    # Paste is in the runner

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
        if not model: return wx.Point(0,0)
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
        if not model: return wx.Point(0,0)
        speed = CDSPoint(model.GetProperty("speed"), model=model, role="speed")
        return speed
    @speed.setter
    def speed(self, val):
        try:
            val = wx.RealPoint(val[0], val[1])
        except:
            raise ValueError("speed must be a point or a list of two numbers")
        model = self._model
        if not model: return
        model.SetProperty("speed", val)

    @property
    def center(self):
        model = self._model
        if not model: return wx.Point(0,0)
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
    def FlipHorizontal(self):
        model = self._model
        if not model: return
        model.PerformFlips(True, False)

    @RunOnMainAsync
    def FlipVertical(self):
        model = self._model
        if not model: return
        model.PerformFlips(False, True)

    @RunOnMainSync
    def OrderToFront(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(-1)

    @RunOnMainSync
    def OrderForward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(1)

    @RunOnMainSync
    def OrderBackward(self):
        model = self._model
        if not model: return
        model.OrderMoveBy(-1)

    @RunOnMainSync
    def OrderToBack(self):
        model = self._model
        if not model: return
        model.OrderMoveTo(0)

    def OrderToIndex(self, i):
        if not isinstance(i, int):
            raise TypeError("OrderToIndex(): index must be a number")

        model = self._model
        if not model: return

        if i < 0 or i >= len(model.parent.childModels):
            raise TypeError("OrderToIndex(): index is out of bounds")

        @RunOnMainSync
        def f():
            if model.didSetDown: return
            model.OrderMoveTo(i)
        f()

    def Show(self):
        self.visible = True
    def Hide(self):
        self.visible = False

    @property
    def visible(self):
        model = self._model
        if not model: return False
        return not model.IsHidden()
    @visible.setter
    def visible(self, val):
        model = self._model
        if not model: return
        model.SetProperty("hidden", not bool(val))

    @property
    def rotation(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("rotation")
    @rotation.setter
    def rotation(self, val):
        if self._model.GetProperty("rotation") == None:
            raise TypeError("object does not support rotation")
        if not isinstance(val, (int, float)):
            raise TypeError("rotation must be a number")
        model = self._model
        if not model: return
        model.SetProperty("rotation", val)

    def GetEventHandler(self, eventName):
        model = self._model
        if not model: return ""
        return model.handlers[eventName]

    def SetEventHandler(self, eventName, code):
        model = self._model
        if not model: return
        if not isinstance(eventName, str):
            raise TypeError("SetEventHandler(): eventName must be a string")
        if not isinstance(code, str):
            raise TypeError("SetEventHandler(): code must be a string")
        if eventName not in model.handlers:
            raise TypeError(f"SetEventHandler(): this object has no event handler called '{eventName}'")

        model.handlers[eventName] = code

    def SetBounceObjects(self, objects):
        if not isinstance(objects, (list, tuple)):
            raise TypeError("SetBounceObjects(): objects needs to be a list of cardstock objects")
        models = [o._model for o in objects if isinstance(o, ViewProxy)]
        self._model.SetBounceModels(models)

    def StopHandlingMouseEvent(self):
        self._model.stackManager.runner.StopHandlingMouseEvent()

    def IsTouchingPoint(self, point):
        if not isinstance(point, (wx.Point, wx.RealPoint, CDSPoint, CDSRealPoint, list, tuple)):
            raise TypeError("IsTouchingPoint(): point needs to be a point or a list of two numbers")
        if len(point) != 2:
            raise TypeError("IsTouchingPoint(): point needs to be a point or a list of two numbers")
        try:
            int(point[0]), int(point[1])
        except:
            raise ValueError("IsTouchingPoint(): point needs to be a point or a list of two numbers")

        model = self._model
        if not model: return False

        @RunOnMainSync
        def f():
            if model.didSetDown: return False
            s = model.stackManager.GetUiViewByModel(model)
            if not s:
                return False
            sreg = s.GetHitRegion()
            return sreg.Contains(wx.Point(point)) == wx.InRegion
        return f()

    def IsTouching(self, obj):
        if not isinstance(obj, ViewProxy):
            raise TypeError("IsTouching(): obj must be a CardStock object")

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

    def IsTouchingEdge(self, obj, skipIsTouchingCheck=False):
        if not isinstance(obj, ViewProxy):
            raise TypeError("IsTouchingEdge(): obj must be a CardStock object")

        model = self._model
        oModel = obj._model
        if not model or not oModel: return None
        ui = model.stackManager.GetUiViewByModel(model)

        @RunOnMainSync
        def f():
            if model.didSetDown or oModel.didSetDown: return None

            if not skipIsTouchingCheck and not self.IsTouching(obj):
                return None

            f = oModel.GetAbsoluteFrame() # other frame in card coords

            reg = ui.GetHitRegion()

            # Pull edge lines away from the corners, so we don't always hit a corner when 2 objects touch
            x_pad = 7 if f.Width > 18 else 0
            y_pad = 7 if f.Height > 18 else 0

            bottom = wx.Rect(f.Left+x_pad, f.Top, f.Width-2*x_pad, 1)
            top = wx.Rect(f.Left+x_pad, f.Bottom-1, f.Width-2*x_pad, 1)
            left = wx.Rect(f.Left, f.Top+y_pad, 1, f.Height-2*y_pad)
            right = wx.Rect(f.Right-1, f.Top+y_pad, 1, f.Height-2*y_pad)
            def intersectTest(r, edge):
                testReg = wx.Region(r)
                testReg.Intersect(edge)
                return not testReg.IsEmpty()

            edges = []
            if intersectTest(reg, top): edges.append("Top")
            if intersectTest(reg, bottom): edges.append("Bottom")
            if intersectTest(reg, left): edges.append("Left")
            if intersectTest(reg, right): edges.append("Right")
            if len(edges) == 0:
                edges = None
            return edges
        return f()

    def AnimatePosition(self, duration, endPosition, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimatePosition(): duration must be a number")
        try:
            endPosition = wx.RealPoint(endPosition)
        except:
            raise ValueError("AnimatePosition(): endPosition must be a point or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origPosition = model.GetAbsolutePosition()
            offsetPt = endPosition - origPosition
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origPosition"] = origPosition
            animDict["offset"] = offset
            model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetAbsolutePosition(animDict["origPosition"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def AnimateCenter(self, duration, endCenter, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateCenter(): duration must be a number")
        try:
            endCenter = wx.RealPoint(endCenter)
        except:
            raise ValueError("AnimateCenter(): endCenter must be a point or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origCenter = model.GetCenter()
            offsetPt = endCenter - origCenter
            offset = wx.RealPoint(offsetPt[0], offsetPt[1])
            animDict["origCenter"] = origCenter
            animDict["offset"] = offset
            self._model.SetProperty("speed", offset*(1.0/duration))

        def onUpdate(progress, animDict):
            model.SetCenter(animDict["origCenter"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            model.SetProperty("speed", (0,0), notify=False)
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        def onCanceled(animDict):
            model.SetProperty("speed", (0,0))

        model.AddAnimation("position", duration, onUpdate, onStart, internalOnFinished, onCanceled)

    def AnimateSize(self, duration, endSize, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateSize(): duration must be a number")
        try:
            endSize = wx.Size(endSize)
        except:
            raise ValueError("AnimateSize(): endSize must be a size or a list of two numbers")

        model = self._model
        if not model: return

        def onStart(animDict):
            origSize = model.GetProperty("size")
            offset = wx.Size(endSize-origSize)
            animDict["origSize"] = origSize
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("size", animDict["origSize"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("size", duration, onUpdate, onStart, internalOnFinished)

    def AnimateRotation(self, duration, endRotation, onFinished=None, forceDirection=0, *args, **kwargs):
        if self._model.GetProperty("rotation") == None:
            raise TypeError("AnimateRotation(): object does not support rotation")

        if not isinstance(duration, (int, float)):
            raise TypeError("AnimateRotation(): duration must be a number")
        if not isinstance(endRotation, (int, float)):
            raise TypeError("AnimateRotation(): endRotation must be a number")
        if not isinstance(forceDirection, (int, float)):
            raise TypeError("AnimateRotation(): forceDirection must be a number")

        model = self._model
        if not model: return

        endRotation = endRotation

        def onStart(animDict):
            origVal = self.rotation
            animDict["origVal"] = origVal
            offset = endRotation - origVal
            if forceDirection:
                if forceDirection > 0:
                    if offset <= 0: offset += 360
                elif forceDirection < 0:
                    if offset >= 0: offset -= 360
            else:
                if offset > 180: offset -= 360
                if offset < -180: offset += 360
            animDict["offset"] = offset

        def onUpdate(progress, animDict):
            model.SetProperty("rotation", (animDict["origVal"] + animDict["offset"] * progress)%360)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("rotation", duration, onUpdate, onStart, internalOnFinished)

    def StopAnimating(self, propertyName=None):
        model = self._model
        if not model: return
        model.StopAnimation(propertyName)
