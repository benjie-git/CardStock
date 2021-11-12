import os
import wx
import generator
import math
from math import pi
from uiView import *


# Utility for rotating image bounding rect
def rotateRad(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class UiImage(UiView):
    """
    This class is a controller that coordinates management of an image view, based on data from an ImageModel.
    An image does not use its own wx.Window as a view, but instead draws itself onto the stack view.
    """

    imgCache = {}

    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model, None)
        self.rotatedBitmap = None
        self.origImage = self.GetImg(model)

    @classmethod
    def ClearCache(cls, path=None):
        if path:
            if path in cls.imgCache:
                del cls.imgCache[path]
        else:
            cls.imgCache = {}

    def AspectStrToInt(self, str):
        if str == "Center":
            return 0
        elif str == "Stretch":
            return 1
        elif str == "Scale":
            return 3
        else:
            return 3 # Default to Scale

    def GetImg(self, model):
        file = model.GetProperty("file")
        filepath = self.stackManager.resPathMan.GetAbsPath(file)

        if filepath in self.imgCache:
            img = self.imgCache[filepath]
        else:
            if filepath and os.path.exists(filepath):
                img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
                self.imgCache[filepath] = img
            else:
                img = None
        return img

    def MakeScaledAndRotatedBitmap(self):
        img = self.origImage
        if not img:
            return None

        xFlipped = self.model.GetProperty("xFlipped")
        yFlipped = self.model.GetProperty("yFlipped")
        rot = self.model.GetProperty("rotation")
        imgSize = img.GetSize()
        viewSize = self.model.GetProperty("size")
        fit = self.model.GetProperty("fit")

        if xFlipped or yFlipped:
            if xFlipped:
                img = img.Mirror(horizontally=True)
            if yFlipped:
                img = img.Mirror(horizontally=False)

        if fit == "Stretch":
            img = img.Scale(viewSize.width, viewSize.height, quality=wx.IMAGE_QUALITY_HIGH)
        elif fit == "Contain":
            scaleX = viewSize.width / imgSize.width
            scaleY = viewSize.height / imgSize.height
            scale = min(scaleX, scaleY)
            img = img.Scale(imgSize.width * scale, imgSize.height * scale, quality=wx.IMAGE_QUALITY_HIGH)
        elif fit == "Fill":
            scaleX = viewSize.width / imgSize.width
            scaleY = viewSize.height / imgSize.height
            scale = max(scaleX, scaleY)
            img = img.Scale(imgSize.width * scale, imgSize.height * scale, quality=wx.IMAGE_QUALITY_HIGH)
            imgSize = img.GetSize()

        if rot != 0:
            val = float(rot * -pi/180)  # make positive value rotate clockwise
            img = img.Rotate(val, list(img.GetSize()/2))   # use original center
            imgSize = img.GetSize()

        if fit in ["Center", "Fill"]:
            offX = 0 if imgSize.Width <= viewSize.Width else ((imgSize.Width - viewSize.Width) / 2)
            offY = 0 if imgSize.Height <= viewSize.Height else ((imgSize.Height - viewSize.Height) / 2)
            w = imgSize.width if imgSize.Width <= viewSize.Width else viewSize.Width
            h = imgSize.height if imgSize.Height <= viewSize.Height else viewSize.Height
            img = img.GetSubImage(wx.Rect(offX, offY, w, h))

        self.rotatedBitmap = img.ConvertToBitmap(32)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)

        if key in ["size", "rotation", "fit", "file", "xFlipped", "yFlipped"]:
            self.rotatedBitmap = None
            self.stackManager.view.Refresh()

        if key == "file":
            self.origImage = self.GetImg(self.model)
            self.rotatedBitmap = None
            self.stackManager.view.Refresh()
        elif key == "fit":
            self.stackManager.view.Refresh()
        elif key == "rotation":
            self.hitRegion = None
            if model.GetProperty("file") != "":
                self.stackManager.view.Refresh()

    def ClearCachedData(self):
        self.rotatedBitmap = None
        self.origImage = None
        self.stackManager.view.Refresh()

    def Paint(self, gc):
        if self.model.GetProperty("file"):
            if not self.origImage:
                self.origImage = self.GetImg(self.model)
            if self.origImage:
                if not self.rotatedBitmap:
                    self.MakeScaledAndRotatedBitmap()
                r = self.model.GetAbsoluteFrame()

                imgSize = self.rotatedBitmap.GetSize()
                viewSize = r.Size
                offX = (viewSize.Width - imgSize.Width) / 2
                offY = (viewSize.Height - imgSize.Height) / 2
                gc.DrawBitmap(self.rotatedBitmap, r.Left + offX, r.Bottom - offY)

        if self.stackManager.isEditing:
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen('Gray', 1, wx.PENSTYLE_DOT))
            rot = self.model.GetProperty("rotation")
            points = self.RotatedRectPoints(self.model.GetAbsoluteFrame(), rot)
            points.append(points[0])
            gc.DrawLines(points)

    def MakeHitRegion(self):
        s = self.model.GetProperty("size")
        rot = self.model.GetProperty("rotation")
        points = self.RotatedRectPoints(wx.Rect(0,0,s.Width+1, s.Height+1), rot)
        points.append(points[0])

        l2 = list(map(list, zip(*points)))
        rotSize = (max(l2[0]) - min(l2[0]), max(l2[1]) - min(l2[1]))
        rotSize = (max(rotSize[0], s[0]), max(rotSize[1], s[1]))
        offset_x = (rotSize[0] - s[0])/2 + 10
        offset_y = (rotSize[1] - s[1])/2 + 10

        bmp = wx.Bitmap(width=rotSize[0]+20, height=rotSize[1]+20, depth=1)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush('black', wx.BRUSHSTYLE_SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush("white", wx.BRUSHSTYLE_SOLID))
        dc.Clear()
        dc.DrawPolygon(points, offset_x, offset_y)

        if self.stackManager.isEditing and self.isSelected and self.stackManager.tool.name == "hand":
            for resizerRect in self.GetResizeBoxRects():
                resizerRect.Offset((offset_x, offset_y))
                dc.DrawRectangle(resizerRect)
        reg = bmp.ConvertToImage().ConvertToRegion(0,0,0)
        reg.Offset(-offset_x, -offset_y)
        self.hitRegion = reg

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen('Blue', 1, wx.PENSTYLE_DOT))
            gc.DrawRectangle(self.model.GetAbsoluteFrame())

            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            rot = self.model.GetProperty("rotation")
            points = self.RotatedRectPoints(f, rot)
            points.append(points[0])
            gc.DrawLines(points)

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            for box in self.GetResizeBoxRects():
                gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def RotatedRectPoints(self, rect, degrees):
        center = rect.TopLeft + rect.Size/2
        points = [rect.TopLeft, rect.TopRight+(1,0), rect.BottomRight+(1,1), rect.BottomLeft+(0,1)]
        points = [wx.Point(rotateRad(center, p, math.radians(-degrees))) for p in points]
        return points


class ImageModel(ViewModel):
    """
    This is the model for an Image object.
    """

    minSize = wx.Size(2, 2)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "image"
        self.proxyClass = Image

        self.properties["name"] = "image_1"
        self.properties["file"] = ""
        self.properties["fit"] = "Contain"
        self.properties["rotation"] = 0
        self.properties["xFlipped"] = False
        self.properties["yFlipped"] = False

        self.propertyTypes["file"] = "file"
        self.propertyTypes["fit"] = "choice"
        self.propertyChoices["fit"] = ["Center", "Stretch", "Contain", "Fill"]
        self.propertyTypes["rotation"] = "int"
        self.propertyTypes["xFlipped"] = "bool"
        self.propertyTypes["yFlipped"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "file", "fit", "rotation", "position", "size"]

    def SetProperty(self, key, value, notify=True):
        if key == "rotation":
            value = value % 360
        super().SetProperty(key, value, notify)

    def PerformFlips(self, fx, fy, notify=True):
        if fx:
            self.SetProperty("xFlipped", not self.GetProperty("xFlipped"), notify=notify)
        if fy:
            self.SetProperty("yFlipped", not self.GetProperty("yFlipped"), notify=notify)


class Image(ViewProxy):
    """
    Image proxy objects are the user-accessible objects exposed to event handler code for image objects.
    """

    @property
    def file(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("file")
    @file.setter
    def file(self, val):
        if not isinstance(val, str):
            raise TypeError("file must be a string")
        model = self._model
        if not model: return
        model.SetProperty("file", val)

    @property
    def rotation(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("rotation")
    @rotation.setter
    def rotation(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("rotation must be a number")
        model = self._model
        if not model: return
        model.SetProperty("rotation", val)

    @property
    def fit(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fit")
    @fit.setter
    def fit(self, val):
        if not isinstance(val, str):
            raise TypeError("fit must be a string")
        model = self._model
        if not model: return
        model.SetProperty("fit", val)

    def AnimateRotation(self, duration, endRotation, onFinished=None, forceDirection=0, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endRotation, (int, float)):
            raise TypeError("endRotation must be a number")
        if not isinstance(forceDirection, (int, float)):
            raise TypeError("forceDirection must be a number")

        model = self._model
        if not model: return

        endRotation = endRotation % 360

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
            model.SetProperty("rotation", animDict["origVal"] + animDict["offset"] * progress)

        def internalOnFinished(animDict):
            if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

        model.AddAnimation("rotation", duration, onUpdate, onStart, internalOnFinished)
