import wx
import generator
from uiView import *


class UiShape(UiView):
    """
    This class is a controller that coordinates management of a shape view, based on data from an LineModel, ShapeModel,
    or RoundRectModel.
    A shape does not use its own wx.Window as a view, but instead draws itself onto the stack view.
    """

    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model, None)

    def DrawShape(self, dc, thickness, penColor, fillColor, offset, points):
        penColor = wx.Colour(penColor)
        if not penColor:
            penColor = wx.Colour('black')

        fillColor = wx.Colour(fillColor)
        if not fillColor:
            fillColor = wx.Colour('white')

        pen = wx.Pen(penColor, thickness, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        if self.model.type in ["pen", "line"]:
            if len(points) > 1:
                dc.DrawLines(points, offset.x, offset.y)
        elif self.model.type in ["oval", "rect", "roundrect"] and len(points) == 2:
            rect = self.model.RectFromPoints(points)
            p1 = rect.TopLeft + offset
            p2 = rect.BottomRight + offset
            if thickness == 0:
                pen = wx.TRANSPARENT_PEN
                dc.SetPen(pen)
            dc.SetBrush(wx.Brush(fillColor, wx.BRUSHSTYLE_SOLID))
            if self.model.type == "rect":
                pen.SetJoin(wx.JOIN_MITER)
                dc.SetPen(pen)
                dc.DrawRectangle(wx.Rect(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1]))
            elif self.model.type == "roundrect":
                radius = self.model.GetProperty("cornerRadius")
                radius = min(radius, abs(p1[0]-p2[0])/2)
                radius = min(radius, abs(p1[1]-p2[1])/2)
                dc.DrawRoundedRectangle(wx.Rect(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1]), radius)
            elif self.model.type == "oval":
                dc.DrawEllipse(wx.Rect(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1]))
        elif self.model.type == "poly" and len(points) >= 2:
            if thickness == 0:
                pen = wx.TRANSPARENT_PEN
                dc.SetPen(pen)
            dc.SetBrush(wx.Brush(fillColor, wx.BRUSHSTYLE_SOLID))
            pen.SetJoin(wx.JOIN_MITER)
            dc.SetPen(pen)
            dc.DrawPolygon(points, offset.x, offset.y)

    def Paint(self, gc):
        thickness = None
        fillColor = None
        penColor = None
        offset = None
        points = None
        with self.model.animLock:
            thickness = self.model.GetProperty("penThickness")
            fillColor = self.model.GetProperty("fillColor")
            penColor = self.model.GetProperty("penColor")
            offset = wx.Point(self.model.GetAbsolutePosition())
            points = self.model.GetScaledPoints()

        self.DrawShape(gc, thickness, penColor, fillColor, offset, points)
        super().Paint(gc)

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = None
            thickness = None
            points = None
            radius = None
            with self.model.animLock:
                f = self.model.GetAbsoluteFrame()
                thickness = self.model.GetProperty("penThickness")
                points = self.model.GetScaledPoints()
                if self.model.type == "roundrect":
                    radius = self.model.GetProperty("cornerRadius")

            f = wx.Rect(f.TopLeft, f.Size - (1,1))
            if wx.Platform != "__WXMAC":
                thickness -=1
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self.model.type in ["line", "pen", "poly"]:
                gc.SetPen(wx.Pen('Blue', 3 + thickness, wx.PENSTYLE_SHORT_DASH))
                if self.model.type == "poly":
                    points.append(points[0])
                if len(points) > 1:
                    gc.DrawLines(points, f.Left, f.Top)
            elif self.model.type == "rect":
                gc.DrawRectangle(wx.Rect(f).Inflate(2 + thickness/2))
            elif self.model.type == "oval":
                gc.DrawEllipse(wx.Rect(f).Inflate(2 + thickness/2))
            elif self.model.type == "roundrect":
                p1 = f.TopLeft
                p2 = f.BottomRight
                radius = min(radius, abs(p1[0]-p2[0])/2)
                radius = min(radius, abs(p1[1]-p2[1])/2)
                gc.DrawRoundedRectangle(wx.Rect(f).Inflate(2 + thickness/2), radius)

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            for box in self.GetResizeBoxRects():
                gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def MakeHitRegion(self):
        if self.model.IsHidden():
            self.hitRegion = wx.Region((0,0), (0,0))

        with self.model.animLock:
            thickness = self.model.GetProperty("penThickness")
            s = self.model.GetProperty("size")
            points = self.model.GetScaledPoints()

        extraThick = 6 if (self.model.type in ["pen", "line"]) else 0
        thickness = thickness + extraThick

        # Draw the region offset up/right, to allow space for bottom/left resize boxes,
        # since they would otherwise be at negative coords, which would be outside the
        # hitRegion bitmap.  Then set the offset of the hitRegion bitmap down/left to make up for it.
        regOffset = (thickness+20)/2

        bmp = wx.Bitmap(width=s.width+2*regOffset, height=s.height+2*regOffset, depth=1)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush('black', wx.BRUSHSTYLE_SOLID))
        dc.Clear()
        penColor = 'white'
        fillColor = 'white'
        self.DrawShape(dc, thickness, penColor, fillColor, wx.Point(regOffset, regOffset), points)
        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            for resizerRect in self.GetResizeBoxRects():
                resizerRect.Offset((regOffset, regOffset))
                dc.DrawRectangle(resizerRect)
        reg = bmp.ConvertToImage().ConvertToRegion(0,0,0)
        reg.Offset(-regOffset, -regOffset)
        self.hitRegion = reg

    def GetResizeBoxRects(self):
        thicknessOffset = self.model.GetProperty("penThickness")/2
        resizerRects = super().GetResizeBoxRects()
        for r in resizerRects:
                r.Offset((thicknessOffset-3 if r.Left >= 0 else -thicknessOffset-2,
                            thicknessOffset-2 if r.Top >= 0 else -thicknessOffset-2))
        return resizerRects

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["size", "shape", "penColor", "penThickness", "fillColor", "cornerRadius"]:
            self.ClearHitRegion()
            self.stackManager.view.Refresh()

    @staticmethod
    def CreateModelForType(stackManager, name):
        if name in ["pen", "line"]:
            return LineModel(stackManager, name)
        if name in ["rect", "oval", "poly"]:
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
        elif shapeType == "poly":
            self.properties["name"] = "polygon_1"
        else:
            self.properties["name"] = f"{shapeType}_1"

        self.properties["originalSize"] = None
        self.properties["penColor"] = "black"
        self.properties["penThickness"] = 2

        self.propertyTypes["originalSize"] = "size"
        self.propertyTypes["penColor"] = "color"
        self.propertyTypes["penThickness"] = "uint"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "position", "size"]

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
        self.properties["penColor"] = shape["penColor"]
        self.properties["penThickness"] = shape["thickness"]
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
        if self.type in ["line", "pen", "poly"]:
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
        return [p + pos for p in self.points]

    @staticmethod
    def RectFromPoints(points):
        rect = wx.Rect(points[0][0], points[0][1], 1, 1)
        for x, y in points[1:]:
            rect = rect.Union(wx.Rect(x, y, 1, 1))
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
                rect = wx.Rect(points[0][0], points[0][1], 1, 1)
            for x,y in points:
                rect = rect.Union(wx.Rect(x, y, 1, 1))

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
    def penColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("penColor")
    @penColor.setter
    def penColor(self, val):
        if not isinstance(val, str):
            raise TypeError("penColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("penColor", val)

    @property
    def penThickness(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("penThickness")
    @penThickness.setter
    def penThickness(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("penThickness must be a number")
        model = self._model
        if not model: return
        model.SetProperty("penThickness", val)

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

    def AnimatePenThickness(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("endThickness must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.penThickness
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("penThickness", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("penThickness", duration, onUpdate, onStart, internalOnFinished)

    def AnimatePenColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)
        if endColor.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.penColor)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("penColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

            def internalOnFinished(animDict):
                if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

            model.AddAnimation("penColor", duration, onUpdate, onStart, internalOnFinished)


class ShapeModel(LineModel):
    """
    This is the model class for Oval and Rectangle objects, and the superclass for models for round-rects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = Shape

        self.properties["fillColor"] = "white"
        self.propertyTypes["fillColor"] = "color"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "fillColor", "position", "size"]

    def SetShape(self, shape):
        self.properties["fillColor"] = shape["fillColor"]
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
            if model.type == "poly":
                return model.GetAbsolutePoints()
            else:
                raise TypeError(f"The points property is not available for shapes of type {model.type}.")
    @points.setter
    def points(self, points):
        model = self._model
        if model and model.parent:
            if model.type == "poly":
                try:
                    points = [wx.RealPoint(p[0], p[1]) for p in points]
                except:
                    raise ValueError("points must be either a list of points, or a list of lists of two numbers")
                model.SetPoints(points)
            else:
                raise TypeError(f"The points property is not available for shapes of type {model.type}.")

    @property
    def fillColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fillColor")
    @fillColor.setter
    def fillColor(self, val):
        if not isinstance(val, str):
            raise TypeError("fillColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fillColor", val)

    def AnimateFillColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)
        if endColor.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.fillColor)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("fillColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

            def internalOnFinished(animDict):
                if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

            model.AddAnimation("fillColor", duration, onUpdate, onStart, internalOnFinished)


class RoundRectModel(ShapeModel):
    """
    This is the model class for Round Rectangle objects.
    """

    def __init__(self, stackManager, shapeType):
        super().__init__(stackManager, shapeType)
        self.proxyClass = RoundRect

        self.properties["cornerRadius"] = 8
        self.propertyTypes["cornerRadius"] = "uint"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "fillColor", "cornerRadius", "position", "size"]

    def SetShape(self, shape):
        self.properties["cornerRadius"] = shape["cornerRadius"] if "cornerRadius" in shape else 8
        super().SetShape(shape)


class RoundRect(Shape):
    """
    RoundRect proxy objects are the user-accessible objects exposed to event handler code for round rect objects.
    They're extended from ShapeProxy, which is extended from the Line proxy class.
    """

    @property
    def cornerRadius(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("cornerRadius")
    @cornerRadius.setter
    def cornerRadius(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("cornerRadius must be a number")
        model = self._model
        if not model: return
        model.SetProperty("cornerRadius", val)

    def AnimateCornerRadius(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("endCornerRadius must be a number")

        model = self._model
        if not model: return

        def onStart(animDict):
            origVal = self.cornerRadius
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("cornerRadius", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("cornerRadius", duration, onUpdate, onStart, internalOnFinished)
