#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Card.

import wx
from uiView import UiView, ViewModel


class UiShapes(UiView):
    def __init__(self, stackView, model=None):
        view = wx.Window(parent=stackView)

        if not model:
            model = ShapesModel()
            model.SetProperty("name", stackView.uiCard.model.GetNextAvailableNameInCard("drawing_"))

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
        for type, color, thickness, line in self.model.shapes:
            pen = wx.Pen(color, thickness, wx.PENSTYLE_SOLID)
            dc.SetPen(pen)

            if type == "pen":
                lastPos = None
                for coords in line:
                    if lastPos:
                        dc.DrawLine(*(lastPos[0], lastPos[1], coords[0], coords[1]))
                    lastPos = coords

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
        self.handlers = {"OnMessage": ""}
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

    def DidUpdateShape(self):  # If client updates the list already passed to AddShape
        self.isDirty = True
        for callback in self.propertyListeners:
            callback(self, "shapes")

