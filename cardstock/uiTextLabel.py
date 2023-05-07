# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from appCommands import SetPropertyCommand
from uiView import *
from uiTextBase import *
from uiTextField import CDSTextCtrl


class UiTextLabel(UiTextBase):
    """
    This class is a controller that coordinates management of a TextLabel view, based on data from a TextLabelModel.
    """

    def __init__(self, parent, stackManager, model):
        self.lastFontSize = None
        self.lastDidShrink = False
        super().__init__(parent, stackManager, model, None)
        self.UpdateFont(model, None)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key in ["text", "font", "font_size", "size", "can_auto_shrink"]:
            self.lastFontSize = None

    def StartInlineEditing(self):
        # Show a temporary StyledTextCtrl with the same frame and font as the label
        text = self.model.GetProperty("text")

        alignment = wx.TE_LEFT
        if self.model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif self.model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        field = CDSTextCtrl(parent=self.stackManager.view, style=wx.TE_MULTILINE | alignment)
        s = self.model.GetProperty("size")
        rect = wx.Rect(wx.Point(tuple(int(x) for x in self.model.GetAbsoluteCenter()-tuple(s/2))), s).Inflate(2)
        rect.width += 20
        rect = self.stackManager.ConvRect(rect)
        field.SetRect(rect)
        field.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        field.Bind(stc.EVT_STC_ZOOM, self.OnZoom)
        field.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        self.UpdateFont(self.model, field)
        if self.view:
            self.view.Hide()
        field.ChangeValue(text)
        field.EmptyUndoBuffer()
        field.SetFocus()
        field.SelectAll()
        self.inlineEditor = field
        self.isInlineEditing = True
        self.stackManager.inlineEditingView = self

    def StopInlineEditing(self, notify=True):
        if self.stackManager.isEditing and self.isInlineEditing:
            if self.view:
                self.view.Show()
            command = SetPropertyCommand(True, "Set Property", self.stackManager.designer.cPanel, self.stackManager.cardIndex, self.model,
                                         "text", self.inlineEditor.GetValue())
            self.stackManager.command_processor.Submit(command)
            self.stackManager.view.RemoveChild(self.inlineEditor)
            wx.CallAfter(self.inlineEditor.Destroy)
            self.inlineEditor = None
            self.isInlineEditing = False
            self.stackManager.inlineEditingView = None
            self.stackManager.view.SetFocus()
            self.stackManager.view.Refresh()

    def DoesTextFitWithSize(self, gc, font_size):
        font = wx.Font(self.font)
        font.SetPixelSize(wx.Size(0, self.stackManager.view.FromDIP(font_size)))
        gc.SetFont(font)
        (width, height) = self.model.GetProperty("size")
        lines = wordwrap(self.model.GetProperty("text"), width, gc)
        extraLineSpacing = 1.25 if wx.Platform == "__WXMSW__" else 1.1
        lineHeight = int(font_size * extraLineSpacing)
        numLines = len(lines.split('\n'))
        return height > lineHeight * numLines

    def GetFontSizeFit(self, gc):
        if self.lastFontSize is not None:
            return (self.lastFontSize, self.lastDidShrink)
        font_size = self.ScaleFontSize(self.model.GetProperty("font_size"), None)
        if self.DoesTextFitWithSize(gc, font_size):
            self.lastFontSize = font_size
            self.lastDidShrink = False
            return (font_size, False)
        self.lastFontSize = self.FindFittingFontSize(gc, 1, font_size)
        self.lastDidShrink = True
        return (self.lastFontSize, True)

    def FindFittingFontSize(self, gc, lower, upper):
        font_size = int((upper + lower) / 2)
        if lower+1 < upper:
            if self.DoesTextFitWithSize(gc, font_size):
                return self.FindFittingFontSize(gc, font_size, upper)
            else:
                return self.FindFittingFontSize(gc, lower, font_size-1)
        else:
            return lower

    def Paint(self, gc):
        dipScale = self.stackManager.view.FromDIP(1000)/1000.0
        align = self.model.GetProperty("alignment")
        (width, height) = self.model.GetProperty("size")

        font = wx.Font(self.font)
        font_size = self.ScaleFontSize(self.model.GetProperty("font_size"), None)

        didShrink = False
        if self.model.GetProperty("can_auto_shrink"):
            (font_size, didShrink) = self.GetFontSizeFit(gc)

        # Shouldn't need to double FromDIP the size here... wx Bug?
        font_size = self.stackManager.view.FromDIP(self.stackManager.view.FromDIP(font_size))
        font.SetPixelSize(wx.Size(0, font_size))

        width *= dipScale

        gc.SetFont(font)
        gc.SetTextForeground(wx.Colour(self.text_color))
        lines = wordwrap(self.model.GetProperty("text"), width, gc)

        offsetY = height * dipScale
        extraLineSpacing = 1.25 if wx.Platform == "__WXMSW__" else 1.1
        lineHeight = int(font_size / dipScale * extraLineSpacing)

        for line in lines.split('\n'):
            line = line.rstrip()
            if align in ["Center", "Right"]:
                textWidth = gc.GetTextExtent(line).Width
                if align == "Center":
                    xPos = (width - textWidth)/2/dipScale
                else:
                    xPos = (width - textWidth)/dipScale
            else:
                xPos = 0

            if wx.Platform == "__WXMSW__":
                gc.DrawText(line, wx.Point(int(xPos), self.stackManager.view.ToDIP(int(offsetY))))
            else:
                gc.DrawText(line, wx.Point(int(xPos), int(offsetY)))

            if offsetY < lineHeight * 9 / 5:  # Don't clip a line due to the extra line spacing
                break

            offsetY -= lineHeight


        if self.stackManager.isEditing:
            self.PaintBoundingBox(gc, 'red' if didShrink else 'gray')


class TextLabelModel(TextBaseModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textlabel"
        self.proxyClass = TextLabel
        self.properties["name"] = "label_1"
        self.properties["can_auto_shrink"] = True
        self.properties["rotation"] = 0.0

        self.propertyTypes["can_auto_shrink"] = "bool"
        self.propertyTypes["rotation"] = "float"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "font_size", "text_color", "can_auto_shrink", "position", "size", "rotation"]


class TextLabel(TextBaseProxy):
    """
    TextLabel proxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    @property
    def can_auto_shrink(self):
        model = self._model
        if not model: return False
        return model.GetProperty("can_auto_shrink")
    @can_auto_shrink.setter
    def can_auto_shrink(self, val):
        model = self._model
        if not model: return
        model.SetProperty("can_auto_shrink", bool(val))


def wordwrap(text, width, dc):
    """
    CardStock -- Bug-Fixed and simplified wx.lib.wordwrap
    Returns a copy of text with newline characters inserted where long
    lines should be broken such that they will fit within the given
    width, on the given `wx.DC` using its current font settings.
    """

    wrapped_lines = []
    text = text.split('\n')
    for line in text:
        pte = dc.GetPartialTextExtents(line)
        idx = 0
        start = 0
        startIdx = 0
        spcIdx = -1
        while idx < len(pte):
            # remember the last seen space
            if line[idx] == ' ':
                spcIdx = idx

            # have we reached the max width?
            if pte[idx] - start > width:
                if spcIdx != -1:
                    idx = min(spcIdx + 1, len(pte) - 1)
                wrapped_lines.append(line[startIdx : idx])
                start = pte[idx-1]
                startIdx = idx
                spcIdx = -1

            idx += 1

        wrapped_lines.append(line[startIdx : idx])

    return '\n'.join(wrapped_lines)
