# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from uiView import *
from embeddedImages import radio_on, radio_off, checkbox_on, checkbox_off
from uiTextLabel import wordwrap

# Native Button Mouse event positions on Mac are offset (?!?)
MAC_BUTTON_OFFSET_HACK = wx.Point(6,4)


class UiButton(UiView):
    """
    This class is a controller that coordinates management of a Button view, based on data from a ButtonModel.
    """
    radioOnBmp = None
    radioOffBmp = None
    checkboxOnBmp = None
    checkboxOffBmp = None

    def __init__(self, parent, stackManager, model):
        self.stackManager = stackManager
        super().__init__(parent, stackManager, model, None)
        self.mouseDownInside = False
        if not UiButton.radioOnBmp:
            UiButton.radioOnBmp = radio_on.GetBitmap()
            UiButton.radioOffBmp = radio_off.GetBitmap()
            UiButton.checkboxOnBmp = checkbox_on.GetBitmap()
            UiButton.checkboxOffBmp = checkbox_off.GetBitmap()
            if wx.Platform != "__WXMSW__":
                def rescale(bmp):
                    s = bmp.GetSize()
                    img = bmp.ConvertToImage()
                    img.Rescale(int(s.width/2), int(s.height/2), wx.IMAGE_QUALITY_HIGH)
                    return img.ConvertToBitmap()
                UiButton.radioOnBmp = rescale(UiButton.radioOnBmp)
                UiButton.radioOffBmp = rescale(UiButton.radioOffBmp)
                UiButton.checkboxOnBmp = rescale(UiButton.checkboxOnBmp)
                UiButton.checkboxOffBmp = rescale(UiButton.checkboxOffBmp)

    def GetCursor(self):
        return wx.CURSOR_HAND

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["title", "fill_color", "text_color"]:
            self.stackManager.view.Refresh()
        elif key == "style":
            sm = self.stackManager
            sm.SelectUiView(None)
            sm.LoadCardAtIndex(sm.cardIndex, reload=True)
            sm.SelectUiView(sm.GetUiViewByModel(model))
        elif key == "is_selected":
            if self.view:
                self.view.SetValue(model.GetProperty("is_selected"))
            else:
                self.stackManager.view.Refresh()

    def OnMouseDown(self, event):
        style = self.model.GetProperty("style")
        if not self.stackManager.isEditing:
            self.mouseDownInside = True
            self.model.mouseStillInside = True
            self.stackManager.view.Refresh()
            if style == "Radio":
                self.model.SetProperty("is_selected", True)
            elif style == "Checkbox":
                self.model.SetProperty("is_selected", not self.model.GetProperty("is_selected"))
        super().OnMouseDown(event)

    def OnMouseEnter(self, event):
        if self.mouseDownInside:
            self.model.mouseStillInside = True
            self.stackManager.view.Refresh()
        super().OnMouseEnter(event)

    def OnMouseExit(self, event):
        if self.mouseDownInside:
            self.model.mouseStillInside = False
            self.stackManager.view.Refresh()
        super().OnMouseExit(event)

    def OnMouseUpOutside(self, event):
        if self.mouseDownInside:
            self.mouseDownInside = False
            if self.stackManager:
                self.stackManager.view.Refresh()

    def OnMouseUp(self, event):
        if self.stackManager and not self.stackManager.isEditing:
            if self.mouseDownInside and self.model.mouseStillInside:
                if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_click"):
                    self.stackManager.runner.RunHandler(self.model, "on_click", event)
                self.mouseDownInside = False
                self.model.mouseStillInside = False
                self.stackManager.view.Refresh()
        super().OnMouseUp(event)

    def Paint(self, gc):
        style = self.model.GetProperty("style")

        hilighted = self.mouseDownInside and self.model.mouseStillInside
        fd = self.stackManager.view.FromDIP
        td = self.stackManager.view.ToDIP
        if style == "Border":
            (width, height) = self.model.GetProperty("size")

            # Draw shadow round rect
            gc.SetPen(wx.Pen('#00000044', fd(1)))
            gc.SetBrush(wx.Brush('#00000044'))
            gc.DrawRoundedRectangle(wx.Rect(1, 0, width-1, height-1), 5)
            # Draw foreground round rect
            gc.SetPen(wx.Pen('#444444', fd(1)))
            gc.SetBrush(wx.Brush('#CCCCCC' if hilighted else self.model.GetProperty("fill_color")))
            gc.DrawRoundedRectangle(wx.Rect(0, 1, width-1, height-1), 5)

            title = self.model.GetProperty("text")
            if len(title):
                font = wx.Font(wx.FontInfo(wx.Size(0, fd(fd(16)))).Family(wx.FONTFAMILY_DEFAULT))
                lineHeight = td(font.GetPixelSize().height)
                (startX, startY) = (0, (height+lineHeight)/2 + (1 if fd(100) == 100 else fd(-3)))

                lines = wordwrap(title, fd(width), gc)
                line = lines.split("\n")[0]

                gc.SetFont(font)
                gc.SetTextForeground(wx.Colour(self.model.GetProperty("text_color")))
                textWidth = gc.GetTextExtent(line).Width
                xPos = (startX + (width - td(textWidth)) / 2)
                gc.DrawText(line, wx.Point(int(xPos), int(startY)))

        elif style == "Borderless":
            title = self.model.GetProperty("text")
            if len(title):
                (width, height) = self.model.GetProperty("size")
                font = wx.Font(wx.FontInfo(wx.Size(0, fd(fd(16)))).Family(wx.FONTFAMILY_DEFAULT))
                lineHeight = td(font.GetPixelSize().height)
                (startX, startY) = (0, (height+lineHeight)/2 + (1 if fd(100) == 100 else fd(-3)))

                lines = wordwrap(title, fd(width), gc)
                line = lines.split("\n")[0]

                gc.SetFont(font)
                gc.SetTextForeground(wx.Colour('#888888' if hilighted else self.model.GetProperty("text_color")))
                textWidth = gc.GetTextExtent(line).Width
                xPos = (startX + (width - td(textWidth)) / 2)
                gc.DrawText(line, wx.Point(int(xPos), int(startY)))

        elif style in ("Radio", "Checkbox"):
            (width, height) = self.model.GetProperty("size")

            if style == "Radio":
                iconBmp = UiButton.radioOnBmp if self.model.GetProperty("is_selected") else UiButton.radioOffBmp
            else:
                iconBmp = UiButton.checkboxOnBmp if self.model.GetProperty("is_selected") else UiButton.checkboxOffBmp
            startY = int((height + iconBmp.Height) / 2) + (1 if fd(100) == 100 else fd(-3))
            gc.DrawBitmap(iconBmp, fd(2), startY)

            title = self.model.GetProperty("text")
            if len(title):
                font = wx.Font(wx.FontInfo(wx.Size(0, fd(fd(16)))).Family(wx.FONTFAMILY_DEFAULT))
                lineHeight = td(font.GetPixelSize().height)
                startY = int((height + lineHeight) / 2) + (1 if fd(100) == 100 else fd(-3))
                startPos = (25, startY)
                gc.SetFont(font)
                gc.SetTextForeground(wx.Colour(self.model.GetProperty("text_color")))
                lines = wordwrap(title, fd(width-25), gc)
                line = lines.split("\n")[0]
                gc.DrawText(line, startPos)

        super().Paint(gc)


class ButtonModel(ViewModel):
    """
    This is the model for a Button object.
    """

    minSize = wx.Size(34,20)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "button"
        self.proxyClass = Button
        self.mouseStillInside = False

        # Add custom handlers to the top of the list
        handlers = {"on_setup": "",
                    "on_click": "",
                    "on_selection_changed": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_click"

        self.properties["name"] = "button_1"
        self.properties["text"] = "Button"
        self.properties["style"] = "Border"
        self.properties["fill_color"] = "white"
        self.properties["text_color"] = "black"
        self.properties["is_selected"] = False
        self.properties["rotation"] = 0.0

        self.propertyTypes["text"] = "string"
        self.propertyTypes["style"] = "choice"
        self.propertyTypes["fill_color"] = "color"
        self.propertyTypes["text_color"] = "color"
        self.propertyTypes["is_selected"] = "bool"
        self.propertyTypes["rotation"] = "float"

        self.UpdatePropKeys(self.properties["style"])

    def SetProperty(self, key, value, notify=True):
        if key == "style":
            self.UpdatePropKeys(value)
        elif key == "is_selected":
            if value != self.GetProperty("is_selected"):
                if value:
                    for m in self.get_radio_group():
                        if m.GetProperty("is_selected") and m != self:
                            m.SetProperty("is_selected", False)
                if self.stackManager and not self.stackManager.isEditing:
                    if not self.stackManager.isEditing and self.stackManager.runner and self.GetHandler("on_selection_changed"):
                        self.stackManager.runner.RunHandler(self, "on_selection_changed", None, value)
        super().SetProperty(key, value, notify)

    def UpdatePropKeys(self, style):
        # Custom property order and mask for the inspector
        if style in ("Border", "Borderless"):
            if style == "Border":
                self.propertyKeys = ["name", "text", "style", "fill_color", "text_color", "rotation", "position", "size"]
            else:
                self.propertyKeys = ["name", "text", "style", "text_color", "rotation", "position", "size"]
            self.initialEditHandler = "on_click"
            if "on_click" not in self.visibleHandlers:
                self.visibleHandlers.add("on_click")
            if "on_selection_changed" in self.visibleHandlers and len(self.handlers["on_selection_changed"]) == 0:
                self.visibleHandlers.remove("on_selection_changed")
        else:
            self.propertyKeys = ["name", "text", "style", "text_color", "is_selected", "rotation", "position", "size"]
            self.initialEditHandler = "on_selection_changed"
            if "on_selection_changed" not in self.visibleHandlers:
                self.visibleHandlers.add("on_selection_changed")
            if "on_click" in self.visibleHandlers and len(self.handlers["on_click"]) == 0:
                self.visibleHandlers.remove("on_click")

    def get_radio_group(self):
        g = []
        if self.GetProperty("style") == "Radio" and self.parent:
            for m in self.parent.childModels:
                if m.type == "button" and m.GetProperty("style") == "Radio":
                    g.append(m)
        return g

    def get_radio_group_selection(self):
        g = self.get_radio_group()
        for m in g:
            if m.GetProperty("is_selected"):
                return m
        return None


class Button(ViewProxy):
    """
    Button proxy objects are the user-accessible objects exposed to event handler code for button objects.
    Based on ProxyView, and adds title, border, and Click().
    """

    @property
    def text(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("text")
    @text.setter
    def text(self, val):
        model = self._model
        if not model: return
        model.SetProperty("text", str(val))

    @property
    def style(self):
        model = self._model
        if not model: return False
        return model.GetProperty("style")
    @style.setter
    def style(self, val):
        model = self._model
        if not model: return
        model.SetProperty("style", bool(val))

    @property
    def fill_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("fill_color")
    @fill_color.setter
    def fill_color(self, val):
        model = self._model
        if not model: return
        model.SetProperty("fill_color", str(val))

    @property
    def text_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("text_color")
    @text_color.setter
    def text_color(self, val):
        model = self._model
        if not model: return
        model.SetProperty("text_color", str(val))

    @property
    def is_selected(self):
        model = self._model
        if not model: return False
        if model.GetProperty("style") in ("Border", "Borderless"):
            return False
        return model.GetProperty("is_selected")
    @is_selected.setter
    def is_selected(self, val):
        model = self._model
        if not model: return
        if model.GetProperty("style") not in ("Border", "Borderless"):
            model.SetProperty("is_selected", bool(val))

    @property
    def is_pressed(self):
        model = self._model
        if not model: return False
        return model.mouseStillInside

    def click(self):
        model = self._model
        if not model: return
        if not model.stackManager.isEditing and model.stackManager.runner and model.GetHandler("on_click"):
            model.stackManager.runner.RunHandler(model, "on_click", None)

    def get_radio_group(self):
        model = self._model
        if not model: return []
        return [m.GetProxy() for m in model.get_radio_group()]

    def get_radio_group_selection(self):
        model = self._model
        if model:
            m = model.get_radio_group_selection()
            if m:
                return m.GetProxy()
        return None
