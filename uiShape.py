#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
import generator
from uiView import *


class UiShape(UiView):
    def __init__(self, parent, stackView, shapeType, model=None):
        view = generator.TransparentWindow(parent=parent.view)
        # self.needsUpdate = True
        # self.buffer = None

        if not model:
            model = self.CreateModelForType(stackView, shapeType)
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("shape_"), False)

        super().__init__(parent, stackView, model, view)

    def SetView(self, view):
        super().SetView(view)
        view.SetBackgroundColour(None)
        view.Bind(wx.EVT_PAINT, self.OnPaint)

    def DrawShape(self, dc):
        thickness = self.model.GetProperty("penThickness")
        pen = wx.Pen(self.model.GetProperty("penColor"), thickness, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        points = self.model.GetScaledPoints()

        if self.model.type in ["pen", "line"]:
            lastPos = points[0]
            for coords in points:
                dc.DrawLine(lastPos[0], lastPos[1], coords[0], coords[1])
                lastPos = coords
        elif len(points) == 2:
            rect = self.model.RectFromPoints(points)
            p1 = rect.TopLeft
            p2 = rect.BottomRight
            if thickness == 0:
                dc.SetPen(wx.Pen("white", 0, wx.PENSTYLE_TRANSPARENT))
            fillColor = self.model.GetProperty("fillColor")
            dc.SetBrush(wx.Brush(fillColor, wx.BRUSHSTYLE_SOLID))
            if self.model.type == "rect":
                pen.SetJoin(wx.JOIN_MITER)
                dc.SetPen(pen)
                dc.DrawRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
            elif self.model.type == "round_rect":
                dc.DrawRoundedRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1],
                                        self.model.GetProperty("cornerRadius"))
            elif self.model.type == "oval":
                dc.DrawEllipse(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])

    # def UpdateBuffer(self):
    #     size = self.view.GetSize()
    #     self.buffer = wx.Bitmap.FromRGBA(max(1,size.width), max(1,size.height))
    #     bdc = wx.BufferedDC(None, self.buffer)
    #     dc = wx.GCDC(bdc)
    #     self.DrawShape(dc)
    #     self.needsUpdate = False
    #
    # def OnResize(self, event):
    #     super().OnResize(event)
    #     self.needsUpdate = True

    def OnPaint(self, event):
        # if self.needsUpdate:
        #     self.UpdateBuffer()
        # wx.BufferedPaintDC(self.view, self.buffer)
        dc = wx.PaintDC(self.view)
        self.DrawShape(dc)
        event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["shape", "penColor", "penThickness", "fillColor", "cornerRadius"]:
            # self.needsUpdate = True
            self.view.Refresh()
            self.view.Update()

    @staticmethod
    def CreateModelForType(stackView, name):
        if name == "pen" or name == "line":
            return LineModel(stackView)
        if name == "rect" or name == "oval":
            return ShapeModel(stackView)
        if name == "round_rect":
            return RoundRectModel(stackView)


class LineModel(ViewModel):
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

    # scale from originalSize to Size
    # take into account thickness/2 border on each side
    def GetScaledPoints(self):
        if self.scaledPoints:
            return self.scaledPoints
        if not self.properties["originalSize"] or self.properties["originalSize"][0] == 0 or self.properties["originalSize"][1] == 0:
            return self.points
        padding = int(self.properties["penThickness"] / 2 + 0.5)
        scaleX = 1
        scaleY = 1
        if (self.properties["originalSize"][0] - 2*padding) != 0:
            scaleX = (self.properties["size"][0] - 2*padding) / (self.properties["originalSize"][0] - 2*padding)
        if (self.properties["originalSize"][1] - 2*padding) != 0:
            scaleY = (self.properties["size"][1] - 2*padding) / (self.properties["originalSize"][1] - 2*padding)
        self.scaledPoints = [(((p[0] - padding) * scaleX) + padding, ((p[1] - padding) * scaleY) + padding) for p in self.points]
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

        padding = max(1, int(self.properties["penThickness"] / 2 + 0.5))
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
                rect = wx.Rect(self.points[0][0]-padding, self.points[0][1]-padding, max(1,padding*2), max(1,padding*2))
            for x,y in self.points:
                rect = rect.Union(wx.Rect(x-padding, y-padding, padding*2, padding*2))

        rect = wx.Rect(rect.Left, rect.Top, rect.Width, rect.Height)

        # adjust view rect
        self.SetProperty("position", rect.Position)
        offset = padding*2 - self.oldThickness
        if rect.Width < 20: rect.Width = 20
        if rect.Height < 20: rect.Height = 20

        if oldSize:
            self.SetProperty("size", [oldSize[0] + offset, oldSize[1] + offset])
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


class RoundRectModel(ShapeModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "round_rect"
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
