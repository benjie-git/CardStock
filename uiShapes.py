#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel


class UiShapes(UiView):
    def __init__(self, stackView, model=None):
        view = wx.Window(parent=stackView)

        if not model:
            model = ShapesModel()
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("shape_"))

        super().__init__(stackView, model, view)

    def SetView(self, view):
        super().SetView(view)
        view.SetBackgroundColour(None)
        view.Bind(wx.EVT_PAINT, self.OnPaint)
        if not self.stackView.isEditing:
            view.Enable(False)

    def DrawShapes(self, dc):
        """
        Redraws all the shapes that have been drawn already.
        """
        for shape in self.model.shapes:
            pen = wx.Pen(shape["penColor"], shape["thickness"], wx.PENSTYLE_SOLID)
            dc.SetPen(pen)

            if shape["type"] == "pen":
                lastPos = None
                for coords in shape["points"]:
                    if lastPos:
                        dc.DrawLine(lastPos[0], lastPos[1], coords[0], coords[1])
                    lastPos = coords
            elif len(shape["points"]) == 2:
                if shape["type"] == "line":
                    p1 = shape["points"][0]
                    p2 = shape["points"][1]
                    dc.DrawLine(p1[0], p1[1], p2[0], p2[1])
                else:
                    rect = self.model.RectFromPoints(shape["points"])
                    p1 = rect.TopLeft
                    p2 = rect.BottomRight
                    fillColor = shape["fillColor"] if "fillColor" in shape else "white"
                    dc.SetBrush(wx.Brush(fillColor, wx.BRUSHSTYLE_SOLID))
                    if shape["type"] == "rect":
                        pen.SetJoin(wx.JOIN_MITER)
                        dc.SetPen(pen)
                        dc.DrawRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
                    elif shape["type"] == "round_rect":
                        dc.DrawRoundedRectangle(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1], 8)
                    elif shape["type"] == "oval":
                        dc.DrawEllipse(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])

    def OnPaint(self, event):
        dc = wx.PaintDC(self.view)
        self.DrawShapes(dc)
        event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "shapes":
            self.view.Refresh()
            self.view.Update()


class ShapesModel(ViewModel):
    def __init__(self):
        super().__init__()
        self.type = "shapes"
        self.handlers = {"OnMessage": "", "OnIdle": ""}
        self.shapes = []

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "position", "size"]

    def GetData(self):
        data = super().GetData()
        data["shapes"] = self.shapes.copy()
        return data

    def SetData(self, data):
        super().SetData(data)
        self.shapes = data["shapes"]

    def AddShape(self, shape):
        self.shapes.append(shape)
        self.isDirty = True
        for callback in self.propertyListeners:
            callback(self, "shapes")

    def UpdateShape(self, i, shape):
        self.shapes[i] = shape
        self.isDirty = True
        for callback in self.propertyListeners:
            callback(self, "shapes")

    def DidUpdateShapes(self):  # If client updates the list already passed to AddShape
        self.isDirty = True
        for callback in self.propertyListeners:
            callback(self, "shapes")

    @staticmethod
    def RectFromPoints(points):
        rect = wx.Rect(points[0][0], points[0][1], 1, 1)
        for x, y in points:
            rect = rect.Union(wx.Rect(x, y, 1, 1))
        return rect

    # Re-fit the bounding box to the shapes
    def ReCropShapes(self):
        # First move all points to be relative to the card origin
        offset = self.GetProperty("position")
        for shape in self.shapes:
            points = shape["points"]
            # adjust all points in shape
            i = 0
            for x, y in points.copy():
                points[i] = (x + offset[0], y + offset[1])
                i += 1

        rect = None
        thickness = 0
        for shape in self.shapes:
            points = shape["points"]
            if len(points) > 0:
                # calculate bounding rect
                if not rect:
                    rect = wx.Rect(points[0][0], points[0][1], 1, 1)
                for x,y in points:
                    rect = rect.Union(wx.Rect(x, y, 1, 1))

                if shape["thickness"] > thickness:
                    thickness = shape["thickness"]

        # inflate rect to account for line thickness
        rect = rect.Inflate(thickness / 2)

        # adjust view rect
        self.SetProperty("position", rect.Position)
        self.SetProperty("size", rect.Size)

        for shape in self.shapes:
            points = shape["points"]
            if len(points) > 0:
                # adjust all points in shape
                i = 0
                for x,y in points.copy():
                    points[i] = (x-rect.Left, y-rect.Top)
                    i += 1

        self.DidUpdateShapes()

    # Un-Crop the shape to fill the card
    def UnCropShape(self, size):
        offset = self.GetProperty("position")
        # adjust view rect
        self.SetProperty("position", [0, 0])
        self.SetProperty("size", size)

        for shape in self.shapes:
            points = shape["points"]
            # adjust all points in shape
            i = 0
            for x, y in points.copy():
                points[i] = (x + offset[0], y + offset[1])
                i += 1
