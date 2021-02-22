#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
import generator
from uiView import *


class UiShape(UiView):
    def __init__(self, parent, stackView, shapeType, model=None):
        if not model:
            model = self.CreateModelForType(stackView, shapeType)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("shape_"), False)

        super().__init__(parent, stackView, model, None)

    def DrawShape(self, dc, thickness, penColor, fillColor, offset):
        pen = wx.Pen(penColor, thickness, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        points = self.model.GetScaledPoints()

        if self.model.type in ["pen", "line"]:
            lastPos = points[0] + offset
            for coords in points:
                coords = coords + offset
                dc.DrawLine(lastPos[0], lastPos[1], coords[0], coords[1])
                lastPos = coords
        elif len(points) == 2:
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
                radius = self.model.GetProperty("cornerRadius")
                radius = min(radius, abs(p1[0]-p2[0])/2)
                radius = min(radius, abs(p1[1]-p2[1])/2)
                dc.DrawRoundedRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1], radius)
            elif self.model.type == "oval":
                dc.DrawEllipse(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])

    def Paint(self, gc):
        thickness = self.model.GetProperty("penThickness")
        fillColor = self.model.GetProperty("fillColor")
        penColor = self.model.GetProperty("penColor")
        offset = wx.Point(self.model.GetAbsolutePosition())
        self.DrawShape(gc, thickness, penColor, fillColor, offset)
        super().Paint(gc)

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackView.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()
            f = wx.Rect(f.TopLeft - wx.Point(1,1), f.Size)
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self.model.type in ["line", "pen"]:
                points = self.model.GetScaledPoints()
                thickness = self.model.GetProperty("penThickness")
                gc.SetPen(wx.Pen('Blue', 3 + thickness, wx.PENSTYLE_SHORT_DASH))
                lastPos = points[0] + f.TopLeft
                for coords in points:
                    coords = coords + f.TopLeft
                    gc.DrawLine(lastPos[0], lastPos[1], coords[0], coords[1])
                    lastPos = coords
            elif self.model.type == "rect":
                gc.DrawRectangle(f.Inflate(2))
            elif self.model.type == "oval":
                gc.DrawEllipse(f.Inflate(2))
            elif self.model.type == "roundrect":
                radius = self.model.GetProperty("cornerRadius")
                gc.DrawRoundedRectangle(f.Inflate(2), radius)
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            box = self.GetResizeBoxRect()
            gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def MakeHitRegion(self):
        s = self.model.GetProperty("size")
        extraThick = 6 if (self.model.type in ["pen", "line"]) else 0
        thickness = self.model.GetProperty("penThickness") + extraThick
        bmp = wx.Bitmap(width=s.width+thickness, height=s.height+thickness, depth=1)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush('black', wx.BRUSHSTYLE_SOLID))
        dc.Clear()
        penColor = 'white'
        fillColor = 'white'
        self.DrawShape(dc, thickness, penColor, fillColor, wx.Point(-thickness/2, -thickness/2))
        f = self.model.GetAbsoluteFrame()
        if self.stackView.isEditing and self.isSelected and self.stackView.tool.name == "hand":
            dc.DrawRectangle(self.GetResizeBoxRect().Inflate(2))
        reg = bmp.ConvertToImage().ConvertToRegion(0,0,0)
        reg.Offset((thickness/2), (thickness/2))
        self.hitRegion = reg

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["size", "shape", "penColor", "penThickness", "fillColor", "cornerRadius"]:
            self.hitRegion = None
            self.stackView.Refresh(True, self.model.GetRefreshFrame())

    @staticmethod
    def CreateModelForType(stackView, name):
        if name == "pen" or name == "line":
            return LineModel(stackView)
        if name == "rect" or name == "oval":
            return ShapeModel(stackView)
        if name == "roundrect":
            return RoundRectModel(stackView)


class LineModel(ViewModel):
    minSize = wx.Size(2, 2)

    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "line"  # Gets rewritten on SetShape (to "line" or "pen")
        self.proxyClass = LineProxy
        self.points = []
        self.scaledPoints = None

        self.properties["originalSize"] = None
        self.properties["penColor"] = ""
        self.properties["penThickness"] = 0
        self.oldThickness = 0

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
        self.oldThickness = self.GetProperty("penThickness")

    def SetShape(self, shape):
        self.type = shape["type"]
        self.properties["penColor"] = shape["penColor"]
        self.properties["penThickness"] = shape["thickness"]
        self.oldThickness = self.GetProperty("penThickness")
        self.points = shape["points"]
        self.isDirty = True
        self.Notify("shape")

    def SetProperty(self, key, value, notify=True):
        super().SetProperty(key, value, notify)
        if key == "size":
            self.scaledPoints = None
        elif key == "penThickness":
            self.ReCropShape()
            self.oldThickness = value

    def DidUpdateShape(self):  # If client updates the points list already passed to AddShape
        self.isDirty = True
        self.scaledPoints = None
        self.Notify("shape")

    def GetRefreshFrame(self):
        return self.GetAbsoluteFrame().Inflate(8 + self.properties["penThickness"])

    # scale from originalSize to Size
    # take into account thickness/2 border on each side
    def GetScaledPoints(self):
        if self.scaledPoints:
            return self.scaledPoints
        if not self.properties["originalSize"] or self.properties["originalSize"][0] == 0 or self.properties["originalSize"][1] == 0:
            return self.points
        scaleX = 1
        scaleY = 1
        if self.properties["originalSize"][0] != 0:
            scaleX = self.properties["size"][0] / self.properties["originalSize"][0]
        if self.properties["originalSize"][1] != 0:
            scaleY = self.properties["size"][1] / self.properties["originalSize"][1]
        self.scaledPoints = [(p[0] * scaleX, p[1] * scaleY) for p in self.points]
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

        oldSize = self.properties["size"] if self.properties["originalSize"] else None

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
        self.SetProperty("position", rect.Position)
        if rect.Width < self.minSize.width: rect.Width = self.minSize.width
        if rect.Height < self.minSize.height: rect.Height = self.minSize.height

        if oldSize:
            self.SetProperty("size", [oldSize[0], oldSize[1]])
        else:
            self.SetProperty("size", rect.Size)
        self.SetProperty("originalSize", rect.Size)

        if len(self.points) > 0:
            # adjust all points in shape
            i = 0
            for x,y in self.points.copy():
                self.points[i] = (x-rect.Left, y-rect.Top)
                i += 1

        self.DidUpdateShape()


class LineProxy(ViewProxy):
    @property
    def penColor(self):
        return self._model.GetProperty("penColor")
    @penColor.setter
    def penColor(self, val):
        self._model.SetProperty("penColor", val)

    @property
    def penThickness(self):
        return self._model.GetProperty("penThickness")
    @penThickness.setter
    def penThickness(self, val):
        self._model.SetProperty("penThickness", val)

    def AnimatePenThickness(self, duration, endVal, onFinished=None):
        origVal = self.penThickness
        if endVal != origVal:
            offset = endVal - origVal
            def f(progress):
                self.penThickness = origVal + offset * progress
            self._model.AddAnimation("penThickness", duration, f, onFinished)
        else:
            self._model.AddAnimation("penThickness", duration, None, onFinished)

    def AnimatePenColor(self, duration, endVal, onFinished=None):
        origVal = wx.Colour(self.penColor)
        endVal = wx.Colour(endVal)
        if origVal.IsOk() and endVal.IsOk() and endVal != origVal:
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            endParts = [endVal.Red(), endVal.Green(), endVal.Blue(), endVal.Alpha()]
            offsets = [endParts[i]-origParts[i] for i in range(4)]
            def f(progress):
                self.penColor = [origParts[i]+offsets[i]*progress for i in range(4)]
            self._model.AddAnimation("penColor", duration, f, onFinished)
        else:
            self._model.AddAnimation("penColor", duration, None, onFinished)


class ShapeModel(LineModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "shape"  # Gets rewritten on SetShape (to "oval" or "rect")
        self.proxyClass = ShapeProxy

        self.properties["fillColor"] = ""
        self.propertyTypes["fillColor"] = "color"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "fillColor", "position", "size"]

    def SetShape(self, shape):
        self.properties["fillColor"] = shape["fillColor"]
        super().SetShape(shape)


class ShapeProxy(LineProxy):
    @property
    def fillColor(self):
        return self._model.GetProperty("fillColor")
    @fillColor.setter
    def fillColor(self, val):
        self._model.SetProperty("fillColor", val)

    def AnimateFillColor(self, duration, endVal, onFinished=None):
        origVal = wx.Colour(self.fillColor)
        endVal = wx.Colour(endVal)
        if origVal.IsOk() and endVal.IsOk() and endVal != origVal:
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            endParts = [endVal.Red(), endVal.Green(), endVal.Blue(), endVal.Alpha()]
            offsets = [endParts[i]-origParts[i] for i in range(4)]
            def f(progress):
                self.fillColor = [origParts[i]+offsets[i]*progress for i in range(4)]
            self._model.AddAnimation("fillColor", duration, f, onFinished)
        else:
            self._model.AddAnimation("fillColor", duration, None, onFinished)


class RoundRectModel(ShapeModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "roundrect"
        self.proxyClass = RoundRectProxy

        self.properties["cornerRadius"] = 8
        self.propertyTypes["cornerRadius"] = "int"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "penColor", "penThickness", "fillColor", "cornerRadius", "position", "size"]

    def SetShape(self, shape):
        self.properties["cornerRadius"] = shape["cornerRadius"] if "cornerRadius" in shape else 8
        super().SetShape(shape)


class RoundRectProxy(ShapeProxy):
    @property
    def cornerRadius(self):
        return self._model.GetProperty("cornerRadius")
    @cornerRadius.setter
    def cornerRadius(self, val):
        self._model.SetProperty("cornerRadius", val)

    def AnimateCornerRadius(self, duration, endVal, onFinished=None):
        origVal = self.cornerRadius
        if endVal != origVal:
            offset = endVal - origVal
            def f(progress):
                self.cornerRadius = origVal + offset * progress
            self._model.AddAnimation("cornerRadius", duration, f, onFinished)
        else:
            self._model.AddAnimation("cornerRadius", duration, None, onFinished)
