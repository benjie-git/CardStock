# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from uiView import *
from imageFactory import ImageFactory

DASHES = {"Solid": wx.PENSTYLE_SOLID,
          "Long-Dashes": wx.PENSTYLE_LONG_DASH,
          "Dashes": wx.PENSTYLE_SHORT_DASH,
          "Dots": wx.PENSTYLE_DOT}


class UiShape(UiView):
    """
    This class is a controller that coordinates management of a shape view, based on data from an LineModel, ShapeModel,
    or RoundRectModel.
    A shape does not use its own wx.Window as a view, but instead draws itself onto the stack view.
    """

    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model, None)
        self.cachedPaths = {}

    def SetDown(self):
        self.cachedPaths = None
        super().SetDown()

    def ClearHitRegion(self, noParent=False):
        super().ClearHitRegion(noParent)
        self.cachedPaths = {}

    def MakeShapePath(self, context, inflate=0):
        # Create a path, un-rotated, in this object's local coords (object.position at 0,0)
        points = self.model.GetScaledPoints()
        shapeType = self.model.type
        path = context.CreatePath()
        if shapeType in ["pen", "line"]:
            if len(points) > 1:
                path.MoveToPoint(*points[0])
                for p in points[1:]:
                    path.AddLineToPoint(*p)
        elif shapeType in ["oval", "rect", "roundrect"] and len(points) == 2:
            rect = self.model.RectFromPoints(points)
            if inflate:
                rect.Inflate(int(inflate))
            p1 = rect.TopLeft
            p2 = rect.BottomRight
            if self.model.type == "rect":
                path.AddRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
            elif self.model.type == "roundrect":
                radius = self.model.GetProperty("corner_radius")
                radius = min(radius, abs(p1[0]-p2[0])/2)
                radius = min(radius, abs(p1[1]-p2[1])/2)
                path.AddRoundedRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1], radius)
            elif self.model.type == "oval":
                path.AddEllipse(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
        elif self.model.type == "polygon" and len(points) >= 2:
            path.MoveToPoint(*points[0])
            for p in points[1:]:
                path.AddLineToPoint(*p)
            path.AddLineToPoint(*points[0])
        return path

    def FlipPath(self, gc, path):
        flipAff = gc.cachedGC.CreateMatrix()
        scale = self.stackManager.view.FromDIP(1000)/1000.0
        if scale != 1.0:
            flipAff.Scale(scale, scale)
        flipAff.Translate(0, self.stackManager.view.Size.Height/scale)
        flipAff.Scale(1, -1)
        path.Transform(flipAff)

    def Paint(self, gc):
        hasFill = self.model.type not in ["line", "pen"]

        with self.model.animLock:
            thickness = self.model.properties["pen_thickness"]
            if hasFill:
                fill_color = self.model.properties["fill_color"]
            pen_color = self.model.properties["pen_color"]

        pen_color = wx.Colour(pen_color)
        if not pen_color:
            pen_color = wx.Colour('black')
        if thickness == 0:
            pen = wx.TRANSPARENT_PEN
        else:
            pen = wx.Pen(pen_color, self.stackManager.view.FromDIP(int(thickness)), DASHES[self.model.properties["pen_style"]])
        gc.cachedGC.SetPen(pen)

        if hasFill:
            pen.SetJoin(wx.JOIN_MITER)
            fill_color = wx.Colour(fill_color)
            if not fill_color:
                fill_color = wx.Colour('white')
            gc.cachedGC.SetBrush(wx.Brush(fill_color, wx.BRUSHSTYLE_SOLID))

        if "paint" in self.cachedPaths:
            path = self.cachedPaths["paint"]
        else:
            path = self.MakeShapePath(gc.cachedGC)
            self.FlipPath(gc, path)
            self.cachedPaths["paint"] = path

        # We're already affine-transformed, so just draw
        if hasFill:
            gc.cachedGC.FillPath(path)
        gc.cachedGC.StrokePath(path)

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            with self.model.animLock:
                thickness = self.model.GetProperty("pen_thickness")
                # s = self.model.GetProperty("size")

            if wx.Platform != "__WXMAC__":
                thickness -= 1

            selThickness = self.stackManager.view.FromDIP(3)
            if (self.model.type in ["pen", "line", "polygon"]):
                # Make lines extra thick for easier clicking
                selThickness += self.stackManager.view.FromDIP(6)
            gc.cachedGC.SetPen(wx.Pen('Blue', selThickness, wx.PENSTYLE_SHORT_DASH))
            gc.cachedGC.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_SOLID))

            # We're already affine-transformed, so just flip vertically and draw
            if "paintSel" in self.cachedPaths:
                path = self.cachedPaths["paintSel"]
            else:
                path = self.MakeShapePath(gc.cachedGC, inflate=(2 + thickness / 2))
                self.FlipPath(gc, path)
                self.cachedPaths["paintSel"] = path
            gc.cachedGC.StrokePath(path)

            if self.model.parent and self.model.parent.type != "group":
                if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
                    for resizerRect in self.GetLocalResizeBoxRects().values():
                        path = gc.cachedGC.CreatePath()
                        path.AddRectangle(resizerRect.Left, resizerRect.Top, resizerRect.Width, resizerRect.Height)
                        self.FlipPath(gc, path)
                        gc.cachedGC.FillPath(path)
                    path = gc.cachedGC.CreatePath()
                    path.AddCircle(*self.GetLocalRotationHandlePoint(), 6)
                    self.FlipPath(gc, path)
                    gc.cachedGC.FillPath(path)

    def MakeHitRegion(self):
        # Make a region in absolute/card coordinates
        if not self.model.IsVisible():
            self.hitRegion = wx.Region((0,0), (0,0))

        with self.model.animLock:
            thickness = self.model.GetProperty("pen_thickness")
            s = self.model.GetProperty("size")
            origPoints = self.model.GetScaledPoints()
            rotRect = self.model.RotatedRect(self.model.RectFromPoints(origPoints))

        if self.model.type in ["pen", "line", "polygon"]:
            # Make lines extra thick for easier clicking
            thickness += 6

        # Draw the region offset up/right, to allow space for bottom/left resize boxes,
        # since they would otherwise be at negative coords, which would be outside the
        # hitRegion bitmap.  Then set the offset of the hitRegion bitmap down/left to make up for it.
        regOffset = (thickness+20)/2 + 24

        height = rotRect.Size[1]+2*regOffset
        img = ImageFactory.shared().GetImage(rotRect.Size[0]+2*regOffset, height)
        context = wx.GraphicsRenderer.GetDefaultRenderer().CreateContextFromImage(img)
        context.SetBrush(wx.Brush('white', wx.BRUSHSTYLE_SOLID))
        context.SetPen(wx.Pen('white', int(thickness), wx.PENSTYLE_SOLID))

        aff = self.model.GetAffineTransform()
        vals = aff.Get()
        # Draw into region bmp rotated but not translated
        vals = (vals[0].m_11, vals[0].m_12, vals[0].m_21, vals[0].m_22, vals[1][0] - (rotRect.Position.x-regOffset), vals[1][1] - (rotRect.Position.y-regOffset))
        aff = context.CreateMatrix(*vals)

        if "hitReg" in self.cachedPaths:
            path = self.cachedPaths["hitReg"]
        else:
            path = self.MakeShapePath(context)
            path.Transform(aff)
            self.cachedPaths["hitReg"] = path

        if self.model.type not in ["line", "pen"]:
            context.FillPath(path)
        context.StrokePath(path)

        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            for resizerRect in self.GetLocalResizeBoxRects().values():
                path = context.CreatePath()
                path.AddRectangle(resizerRect.Left, resizerRect.Top, resizerRect.Width, resizerRect.Height)
                path.Transform(aff)
                context.FillPath(path)
            path = context.CreatePath()
            path.AddCircle(*self.GetLocalRotationHandlePoint(), 6)
            path.Transform(aff)
            context.FillPath(path)
        context.Flush()

        reg = img.ConvertToRegion(0,0,0)
        ImageFactory.shared().RecycleImage(img)
        reg.Offset(int(rotRect.Position.x-regOffset), int(rotRect.Position.y-regOffset))
        self.hitRegion = reg
        self.hitRegionOffset = self.model.GetAbsolutePosition()

    def GetLocalResizeBoxPoints(self):
        thicknessOffset = self.model.GetProperty("pen_thickness")/2
        resizerPoints = super().GetLocalResizeBoxPoints()
        for k,p in resizerPoints.items():
                p += (thicknessOffset-2 if p.x > 0 else -thicknessOffset-2,
                      thicknessOffset-2 if p.y > 0 else -thicknessOffset-2)
        return resizerPoints

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["size", "shape", "pen_color", "pen_thickness", "pen_style",  "fill_color", "corner_radius", "rotation"]:
            self.ClearHitRegion()
            self.stackManager.view.Refresh()
        if key in ["size", "shape", "pen_thickness", "corner_radius", "rotation"]:
            self.cachedPaths = {}

    @staticmethod
    def CreateModelForType(stackManager, name):
        if name in ["pen", "line"]:
            return LineModel(stackManager, name)
        if name in ["rect", "oval", "polygon"]:
            return ShapeModel(stackManager, name)
        if name == "roundrect":
            return RoundRectModel(stackManager, name)


class LineModel(ViewModel):
    """
    This is the model class for Line and Pen objects, and the superclass for models for the other shapes.
    """

    minSize = wx.Size(2, 2)

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager)
        self.type = shapeType
        self.proxyClass = Line
        self.points = []
        self.scaledPoints = None

        if shapeType == "pen":
            self.properties["name"] = "line_1"
        elif shapeType == "polygon":
            self.properties["name"] = "polygon_1"
        else:
            self.properties["name"] = f"{shapeType}_1"

        self.properties["originalSize"] = None
        self.properties["pen_color"] = "black"
        self.properties["pen_style"] = "Solid"
        self.properties["pen_thickness"] = 2
        self.properties["rotation"] = 0.0

        self.propertyTypes["originalSize"] = "size"
        self.propertyTypes["pen_color"] = "color"
        self.propertyTypes["pen_style"] = "choice"
        self.propertyTypes["pen_thickness"] = "uint"
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "pen_color", "pen_thickness", "pen_style", "position", "size", "rotation"]

    def GetData(self):
        data = super().GetData()
        data["points"] = self.points.copy()
        return data

    def SetData(self, data):
        super().SetData(data)
        self.type = data["type"]
        self.points = data["points"]

    def SetShape(self, shape):
        self.type = shape["type"]
        self.properties["pen_color"] = shape["pen_color"]
        self.properties["pen_thickness"] = shape["thickness"]
        self.points = shape["points"]
        self.isDirty = True
        self.Notify("shape")

    def SetProperty(self, key, value, notify=True):
        if self.didSetDown: return
        if key == "size":
            self.scaledPoints = None
        super().SetProperty(key, value, notify)

    def DidUpdateShape(self):  # If client updates the points list already passed to AddShape
        self.isDirty = True
        self.scaledPoints = None
        self.Notify("shape")

    def PerformFlips(self, fx, fy, notify=True):
        super().PerformFlips(fx, fy, notify)
        if self.type in ["line", "pen", "polygon"]:
            if fx or fy:
                origSize = self.properties["originalSize"]
                self.points = [((origSize[0] - p[0]) if fx else p[0], (origSize[1] - p[1]) if fy else p[1]) for p in self.points]
                self.scaledPoints = None
                if notify:
                    self.Notify("size")


    # scale from originalSize to Size
    # take into account thickness/2 border on each side
    def GetScaledPoints(self):
        if self.scaledPoints:
            return self.scaledPoints

        origSize = self.properties["originalSize"]
        size = self.GetProperty("size")

        if not origSize or origSize[0] == 0 or origSize[1] == 0:
            return self.points
        scaleX = 1
        scaleY = 1
        if origSize[0] != 0:
            scaleX = size[0] / origSize[0]
        if origSize[1] != 0:
            scaleY = size[1] / origSize[1]
        points = [(p[0] * scaleX, p[1] * scaleY) for p in self.points]
        self.scaledPoints = points
        return self.scaledPoints

    def GetAbsolutePoints(self):
        pos = self.GetAbsolutePosition()
        return [p + pos for p in self.GetScaledPoints()]

    @staticmethod
    def RectFromPoints(points):
        rect = wx.Rect(int(points[0][0]), int(points[0][1]), 1, 1)
        for x, y in points[1:]:
            rect = rect.Union(wx.Rect(int(x), int(y), 1, 1))
        return wx.Rect(rect.Left, rect.Top, rect.Width-1, rect.Height-1)

    # Re-fit the bounding box to the shape
    def ReCropShape(self):
        if len(self.points) == 0:
            return

        oldSize = self.GetProperty("size") if self.properties["originalSize"] else None

        # First move all points to be relative to the card origin
        offset = self.GetProperty("position")
        points = self.points.copy()
        # adjust all points in shape
        i = 0
        for x, y in points:
            points[i] = (x + offset[0], y + offset[1])
            i += 1

        rect = None
        if len(points) > 0:
            # calculate bounding rect
            if not rect:
                rect = wx.Rect(int(points[0][0]), int(points[0][1]), 1, 1)
            for x,y in points:
                rect = rect.Union(wx.Rect(int(x), int(y), 1, 1))

        rect = wx.Rect(rect.Left, rect.Top, rect.Width-1, rect.Height-1)

        # adjust view rect
        self.SetProperty("position", rect.Position)
        if rect.Width < self.minSize.width: rect.Width = self.minSize.width
        if rect.Height < self.minSize.height: rect.Height = self.minSize.height

        if oldSize:
            self.SetProperty("size", [oldSize[0], oldSize[1]])
        else:
            self.SetProperty("size", rect.Size)
        self.SetProperty("originalSize", rect.Size)

        if len(points) > 0:
            # adjust all points in shape
            i = 0
            for x,y in points:
                points[i] = (x-rect.Left, y-rect.Top)
                i += 1

        self.points = points
        self.DidUpdateShape()

    @RunOnMainSync
    def SetPoints(self, points):
        with self.animLock:
            cardSize = self.GetCard().GetProperty("size")
            self.SetProperty("position", (0,0), notify=False)
            self.SetProperty("size", cardSize, notify=False)
            self.properties["originalSize"] = None
            self.points = points
            self.ReCropShape()


class Line(ViewProxy):
    """
    Line proxy objects are the user-accessible objects exposed to event handler code for line objects.
    """

    @property
    def pen_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("pen_color")
    @pen_color.setter
    def pen_color(self, val):
        if not isinstance(val, str):
            raise TypeError("pen_color must be a string")
        model = self._model
        if not model: return
        model.SetProperty("pen_color", val)

    @property
    def pen_style(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("pen_style")
    @pen_style.setter
    def pen_style(self, val):
        if not isinstance(val, str):
            raise TypeError("pen_style must be one of 'Solid', 'Long-Dashes', 'Dashes', 'Dots'")
        model = self._model
        if not model: return
        model.SetProperty("pen_style", val)

    @property
    def pen_thickness(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("pen_thickness")
    @pen_thickness.setter
    def pen_thickness(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("pen_thickness must be a number")
        model = self._model
        if not model: return
        model.SetProperty("pen_thickness", val)

    @property
    def points(self):
        model = self._model
        if not model or not model.parent: return []
        return model.GetAbsolutePoints()
    @points.setter
    def points(self, points):
        model = self._model
        if not model or not model.parent: return

        try:
            points = [wx.RealPoint(p[0], p[1]) for p in points]
        except:
            raise ValueError("points must be either a list of points, or a list of lists of two numbers")

        model.SetPoints(points)

    def animate_pen_thickness(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_pen_thickness(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("animate_pen_thickness(): end_thickness must be a number")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_pen_thickness(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        def onStart(animDict):
            origVal = self.pen_thickness
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("pen_thickness", animDict["origVal"] + animDict["offset"] * ease(progress, easing))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        model.AddAnimation("pen_thickness", duration, onUpdate, onStart, internalOnFinished)

    def animate_pen_color(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_pen_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_pen_color(): end_color must be a string")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_pen_color(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        end_color = wx.Colour(endVal)
        if end_color.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.pen_color)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("pen_color", wx.Colour([int(animDict["origParts"][i] + animDict["offsets"][i] * ease(progress, easing)) for i in range(4)]))

            def internalOnFinished(animDict):
                if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

            model.AddAnimation("pen_color", duration, onUpdate, onStart, internalOnFinished)


class ShapeModel(LineModel):
    """
    This is the model class for Oval and Rectangle objects, and the superclass for models for round-rects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = Shape

        self.properties["fill_color"] = "white"
        self.propertyTypes["fill_color"] = "color"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "pen_color", "pen_thickness", "pen_style",  "fill_color", "position", "size", "rotation"]

    def SetShape(self, shape):
        self.properties["fill_color"] = shape["fill_color"]
        super().SetShape(shape)


class Shape(Line):
    """
    Shape proxy objects are the user-accessible objects exposed to event handler code for oval and rect objects.
    They're extended from the Line proxy class.
    """

    @property
    def points(self):
        model = self._model
        if model and model.parent:
            if model.type == "polygon":
                return model.GetAbsolutePoints()
            else:
                raise TypeError(f"The points property is not available for shapes of type {model.type}.")
    @points.setter
    def points(self, points):
        model = self._model
        if model and model.parent:
            if model.type == "polygon":
                try:
                    points = [wx.RealPoint(p[0], p[1]) for p in points]
                except:
                    raise ValueError("points must be either a list of points, or a list of lists of two numbers")
                model.SetPoints(points)
            else:
                raise TypeError(f"The points property is not available for shapes of type {model.type}.")

    @property
    def fill_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fill_color")
    @fill_color.setter
    def fill_color(self, val):
        if not isinstance(val, str):
            raise TypeError("fill_color must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fill_color", val)

    def animate_fill_color(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_fill_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_fill_color(): end_color must be a string")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_fill_color(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        end_color = wx.Colour(endVal)
        if end_color.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.fill_color)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("fill_color", wx.Colour([int(animDict["origParts"][i] + animDict["offsets"][i] * ease(progress, easing)) for i in range(4)]))

            def internalOnFinished(animDict):
                if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

            model.AddAnimation("fill_color", duration, onUpdate, onStart, internalOnFinished)


class RoundRectModel(ShapeModel):
    """
    This is the model class for Round Rectangle objects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = RoundRect

        self.properties["corner_radius"] = 8
        self.propertyTypes["corner_radius"] = "uint"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "pen_color", "pen_thickness", "pen_style", "fill_color", "corner_radius", "position", "size", "rotation"]

    def SetShape(self, shape):
        self.properties["corner_radius"] = shape["corner_radius"] if "corner_radius" in shape else 8
        super().SetShape(shape)


class RoundRect(Shape):
    """
    RoundRect proxy objects are the user-accessible objects exposed to event handler code for round rect objects.
    They're extended from ShapeProxy, which is extended from the Line proxy class.
    """

    @property
    def corner_radius(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("corner_radius")
    @corner_radius.setter
    def corner_radius(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("corner_radius must be a number")
        model = self._model
        if not model: return
        model.SetProperty("corner_radius", val)

    def animate_corner_radius(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_corner_radius(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("animate_corner_radius(): end_corner_radius must be a number")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_corner_radius(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        def onStart(animDict):
            origVal = self.corner_radius
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("corner_radius", animDict["origVal"] + animDict["offset"] * ease(progress, easing))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        model.AddAnimation("corner_radius", duration, onUpdate, onStart, internalOnFinished)
