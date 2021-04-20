import wx
import generator
from uiView import *
from killableThread import RunOnMain


class UiShape(UiView):
    """
    This class is a controller that coordinates management of a shape view, based on data from an LineModel, ShapeModel,
    or RoundRectModel.
    A shape does not use its own wx.Window as a view, but instead draws itself onto the stack view.
    """

    def __init__(self, parent, stackManager, shapeType, model=None):
        if not model:
            model = self.CreateModelForType(stackManager, shapeType)
            model.SetProperty("name", stackManager.uiCard.model.GetNextAvailableNameInCard("shape"), notify=False)

        super().__init__(parent, stackManager, model, None)

    def DrawShape(self, dc, thickness, penColor, fillColor, offset):
        penColor = wx.Colour(penColor)
        if not penColor:
            penColor = wx.Colour('black')

        fillColor = wx.Colour(fillColor)
        if not fillColor:
            fillColor = wx.Colour('white')

        pen = wx.Pen(penColor, thickness, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        points = self.model.GetScaledPoints(noDeferred=True)

        if self.model.type in ["pen", "line"]:
            lastPos = points[0] + offset
            lines = []
            for coords in points:
                coords = coords + offset
                lines.append((lastPos[0], lastPos[1], coords[0], coords[1]))
                lastPos = coords
            dc.DrawLineList(lines)
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
                dc.DrawRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
            elif self.model.type == "roundrect":
                radius = self.model.GetProperty("cornerRadius", noDeferred=True)
                radius = min(radius, abs(p1[0]-p2[0])/2)
                radius = min(radius, abs(p1[1]-p2[1])/2)
                dc.DrawRoundedRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1], radius)
            elif self.model.type == "oval":
                dc.DrawEllipse(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
        elif self.model.type == "poly" and len(points) >= 2:
            if thickness == 0:
                pen = wx.TRANSPARENT_PEN
                dc.SetPen(pen)
            dc.SetBrush(wx.Brush(fillColor, wx.BRUSHSTYLE_SOLID))
            pen.SetJoin(wx.JOIN_MITER)
            dc.SetPen(pen)
            dc.DrawPolygon(points, offset.x, offset.y)

    def Paint(self, gc):
        thickness = self.model.GetProperty("penThickness", noDeferred=True)
        fillColor = self.model.GetProperty("fillColor", noDeferred=True)
        penColor = self.model.GetProperty("penColor", noDeferred=True)
        offset = wx.Point(self.model.GetAbsolutePosition(noDeferred=True))
        self.DrawShape(gc, thickness, penColor, fillColor, offset)
        super().Paint(gc)

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()
            f = wx.Rect(f.TopLeft - wx.Point(1,1), f.Size)
            thickness = self.model.GetProperty("penThickness")
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self.model.type in ["line", "pen", "poly"]:
                points = self.model.GetScaledPoints()
                gc.SetPen(wx.Pen('Blue', 3 + thickness, wx.PENSTYLE_SHORT_DASH))
                lastPos = points[0] + f.TopLeft
                lines = []
                for coords in points:
                    coords = coords + f.TopLeft + (1,1)
                    lines.append((lastPos[0], lastPos[1], coords[0], coords[1]))
                    lastPos = coords
                if self.model.type == "poly":
                    first = points[0] + f.TopLeft
                    last = points[-1] + f.TopLeft
                    lines.append((last[0], last[1], first[0], first[1]))
                gc.DrawLineList(lines)
            elif self.model.type == "rect":
                gc.DrawRectangle(f.Inflate(2 + thickness/2))
            elif self.model.type == "oval":
                gc.DrawEllipse(f.Inflate(2 + thickness/2))
            elif self.model.type == "roundrect":
                radius = self.model.GetProperty("cornerRadius")
                p1 = f.TopLeft
                p2 = f.BottomRight
                radius = min(radius, abs(p1[0]-p2[0])/2)
                radius = min(radius, abs(p1[1]-p2[1])/2)
                gc.DrawRoundedRectangle(f.Inflate(2 + thickness/2), radius)

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            box = self.GetResizeBoxRect()
            if self.model.type not in ["line", "pen"]:
                box.Offset((thickness / 2, thickness / 2))
            gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def MakeHitRegion(self):
        if self.model.GetProperty("hidden"):
            self.hitRegion = wx.Region((0,0), (0,0))

        s = self.model.GetProperty("size")
        extraThick = 6 if (self.model.type in ["pen", "line"]) else 0
        thickness = self.model.GetProperty("penThickness") + extraThick
        bmp = wx.Bitmap(width=s.width+thickness+10, height=s.height+thickness+10, depth=1)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush('black', wx.BRUSHSTYLE_SOLID))
        dc.Clear()
        penColor = 'white'
        fillColor = 'white'
        self.DrawShape(dc, thickness, penColor, fillColor, wx.Point(thickness/2, thickness/2))
        f = self.model.GetAbsoluteFrame()
        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            resizerRect = self.GetResizeBoxRect().Inflate(2)
            resizerRect.Offset((thickness/2, thickness/2))
            dc.DrawRectangle(resizerRect)
        reg = bmp.ConvertToImage().ConvertToRegion(0,0,0)
        reg.Offset(-thickness/2, -thickness/2)
        self.hitRegion = reg

    def GetResizeBoxRect(self):
        thickness = self.model.GetProperty("penThickness")
        resizerRect = super().GetResizeBoxRect()
        resizerRect.Offset((thickness/2, thickness/2))
        return resizerRect

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["size", "shape", "penColor", "penThickness", "fillColor", "cornerRadius"]:
            self.ClearHitRegion()
            self.stackManager.view.Refresh(True)

    @staticmethod
    def CreateModelForType(stackManager, name):
        if name in ["pen", "line"]:
            return LineModel(stackManager)
        if name in ["rect", "oval", "poly"]:
            return ShapeModel(stackManager)
        if name == "roundrect":
            return RoundRectModel(stackManager)


class LineModel(ViewModel):
    """
    This is the model class for Line and Pen objects, and the superclass for models for the other shapes.
    """

    minSize = wx.Size(2, 2)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "line"  # Gets rewritten on SetShape (to "line" or "pen")
        self.proxyClass = Line
        self.points = []
        self.scaledPoints = None

        self.properties["originalSize"] = None
        self.properties["penColor"] = "black"
        self.properties["penThickness"] = 2

        self.propertyTypes["originalSize"] = "size"
        self.propertyTypes["penColor"] = "color"
        self.propertyTypes["penThickness"] = "int"

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

    @RunOnMain
    def SetProperty(self, key, value, notify=True, noDeferred=False):
        super().SetProperty(key, value, notify, noDeferred)
        if key == "size":
            self.scaledPoints = None
        elif key == "penThickness":
            self.ReCropShape()

    def DidUpdateShape(self):  # If client updates the points list already passed to AddShape
        self.isDirty = True
        self.scaledPoints = None
        self.Notify("shape")

    def PerformFlips(self, fx, fy):
        if self.type in ["line", "pen", "poly"]:
            if fx or fy:
                origSize = self.properties["originalSize"]
                self.points = [((origSize[0] - p[0]) if fx else p[0], (origSize[1] - p[1]) if fy else p[1]) for p in self.points]
                self.scaledPoints = None
                self.Notify("size")


    # scale from originalSize to Size
    # take into account thickness/2 border on each side
    def GetScaledPoints(self, noDeferred=False):
        if self.scaledPoints:
            return self.scaledPoints
        if not self.properties["originalSize"] or self.properties["originalSize"][0] == 0 or self.properties["originalSize"][1] == 0:
            return self.points
        scaleX = 1
        scaleY = 1
        origSize = self.properties["originalSize"]
        if origSize[0] != 0:
            scaleX = self.GetProperty("size", noDeferred)[0] / origSize[0]
        if origSize[1] != 0:
            scaleY = self.GetProperty("size", noDeferred)[1] / origSize[1]
        points = [(p[0] * scaleX, p[1] * scaleY) for p in self.points]
        self.scaledPoints = points
        return self.scaledPoints

    @staticmethod
    def RectFromPoints(points):
        rect = wx.Rect(points[0][0], points[0][1], 1, 1)
        for x, y in points:
            rect = rect.Union(wx.Rect(x, y, 1, 1))
        return wx.Rect(rect.Left, rect.Top, rect.Width-1, rect.Height-1)

    # Re-fit the bounding box to the shape
    def ReCropShape(self):
        if len(self.points) == 0:
            return

        oldSize = self.GetProperty("size") if self.properties["originalSize"] else None

        # First move all points to be relative to the card origin
        offset = self.GetProperty("position")
        # adjust all points in shape
        i = 0
        for x, y in self.points.copy():
            self.points[i] = (x + offset[0], y + offset[1])
            i += 1

        rect = None
        if len(self.points) > 0:
            # calculate bounding rect
            if not rect:
                rect = wx.Rect(self.points[0][0], self.points[0][1], 1, 1)
            for x,y in self.points:
                rect = rect.Union(wx.Rect(x, y, 1, 1))

        rect = wx.Rect(rect.Left, rect.Top, rect.Width-1, rect.Height-1)

        # adjust view rect
        self.SetProperty("position", rect.Position, noDeferred=True)
        if rect.Width < self.minSize.width: rect.Width = self.minSize.width
        if rect.Height < self.minSize.height: rect.Height = self.minSize.height

        if oldSize:
            self.SetProperty("size", [oldSize[0], oldSize[1]], noDeferred=True)
        else:
            self.SetProperty("size", rect.Size, noDeferred=True)
        self.SetProperty("originalSize", rect.Size, noDeferred=True)

        if len(self.points) > 0:
            # adjust all points in shape
            i = 0
            for x,y in self.points.copy():
                self.points[i] = (x-rect.Left, y-rect.Top)
                i += 1

        self.DidUpdateShape()


class Line(ViewProxy):
    """
    Line proxy objects are the user-accessible objects exposed to event handler code for line objects.
    """

    @property
    def penColor(self):
        return self._model.GetProperty("penColor")
    @penColor.setter
    def penColor(self, val):
        if not isinstance(val, str):
            raise TypeError("penColor must be a string")
        self._model.SetProperty("penColor", val)

    @property
    def penThickness(self):
        return self._model.GetProperty("penThickness")
    @penThickness.setter
    def penThickness(self, val):
        if not (isinstance(val, int) or isinstance(val, float)):
            raise TypeError("penThickness must be a number")
        self._model.SetProperty("penThickness", val)

    def AnimatePenThickness(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        if not (isinstance(endVal, int) or isinstance(endVal, float)):
            raise TypeError("endThickness must be a number")

        @RunOnMain
        def func():
            origVal = self.penThickness

            def internalOnFinished():
                if onFinished: onFinished(*args, **kwargs)

            if endVal != origVal:
                offset = endVal - origVal
                def f(progress):
                    self.penThickness = origVal + offset * progress
                self._model.AddAnimation("penThickness", duration, f, internalOnFinished)
            else:
                self._model.AddAnimation("penThickness", duration, None, internalOnFinished)
        func()

    def AnimatePenColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("endColor must be a string")

        @RunOnMain
        def func():
            origVal = wx.Colour(self.penColor)
            endValue = wx.Colour(endVal)

            def internalOnFinished():
                if onFinished: onFinished(*args, **kwargs)

            if origVal.IsOk() and endValue.IsOk() and endValue != origVal:
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                endParts = [endValue.Red(), endValue.Green(), endValue.Blue(), endValue.Alpha()]
                offsets = [endParts[i]-origParts[i] for i in range(4)]
                def f(progress):
                    self._model.SetProperty("penColor", [origParts[i]+offsets[i]*progress for i in range(4)])
                self._model.AddAnimation("penColor", duration, f, internalOnFinished)
            else:
                self._model.AddAnimation("penColor", duration, None, internalOnFinished)
        func()


class ShapeModel(LineModel):
    """
    This is the model class for Oval and Rectangle objects, and the superclass for models for round-rects.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "shape"  # Gets rewritten on SetShape (to "oval", "rect", or "poly")
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
    def fillColor(self):
        return self._model.GetProperty("fillColor")
    @fillColor.setter
    def fillColor(self, val):
        if not isinstance(val, str):
            raise TypeError("fillColor must be a string")
        self._model.SetProperty("fillColor", val)

    def AnimateFillColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("endColor must be a string")

        @RunOnMain
        def func():
            origVal = wx.Colour(self.fillColor)
            endValue = wx.Colour(endVal)

            def internalOnFinished():
                if onFinished: onFinished(*args, **kwargs)

            if origVal.IsOk() and endValue.IsOk() and endValue != origVal:
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                endParts = [endValue.Red(), endValue.Green(), endValue.Blue(), endValue.Alpha()]
                offsets = [endParts[i]-origParts[i] for i in range(4)]
                def f(progress):
                    self._model.SetProperty("fillColor", [origParts[i]+offsets[i]*progress for i in range(4)])
                self._model.AddAnimation("fillColor", duration, f, internalOnFinished)
            else:
                self._model.AddAnimation("fillColor", duration, None, internalOnFinished)
        func()


class RoundRectModel(ShapeModel):
    """
    This is the model class for Round Rectangle objects.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "roundrect"
        self.proxyClass = RoundRect

        self.properties["cornerRadius"] = 8
        self.propertyTypes["cornerRadius"] = "int"

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
        return self._model.GetProperty("cornerRadius")
    @cornerRadius.setter
    def cornerRadius(self, val):
        if not (isinstance(val, int) or isinstance(val, float)):
            raise TypeError("cornerRadius must be a number")
        self._model.SetProperty("cornerRadius", val)

    def AnimateCornerRadius(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not (isinstance(duration, int) or isinstance(duration, float)):
            raise TypeError("duration must be a number")
        if not (isinstance(endVal, int) or isinstance(endVal, float)):
            raise TypeError("endCornerRadius must be a number")

        @RunOnMain
        def func():
            origVal = self.cornerRadius

            def internalOnFinished():
                if onFinished: onFinished(*args, **kwargs)

            if endVal != origVal:
                offset = endVal - origVal
                def f(progress):
                    self.cornerRadius = origVal + offset * progress
                self._model.AddAnimation("cornerRadius", duration, f, internalOnFinished)
            else:
                self._model.AddAnimation("cornerRadius", duration, None, internalOnFinished)
        func()
