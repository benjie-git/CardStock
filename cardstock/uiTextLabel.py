import wx
from commands import SetPropertyCommand
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
        if key in ["text", "font", "fontSize", "size", "autoShrink"]:
            self.lastFontSize = None

    def StartInlineEditing(self):
        # Show a temporary StyledTextCtrl with the same frame and font as the label
        text = self.model.GetProperty("text")

        alignment = wx.TE_LEFT
        if self.model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif self.model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        field = CDSTextCtrl(parent=self.stackManager.view, size=self.model.GetProperty("size"),
                            pos=self.stackManager.ConvRect(self.model.GetAbsoluteFrame()).BottomLeft,
                            style=wx.TE_MULTILINE | alignment)
        rect = self.model.GetAbsoluteFrame().Inflate(2)
        rect.width += 20
        field.SetRect(self.stackManager.ConvRect(rect))
        field.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        field.Bind(stc.EVT_STC_ZOOM, self.OnZoom)
        field.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        self.UpdateFont(self.model, field)
        if self.view:
            self.view.Hide()
        field.ChangeValue(text)
        field.EmptyUndoBuffer()
        field.SetFocus()
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

    def DoesTextFitWithSize(self, gc, fontSize):
        font = wx.Font(self.font)
        font.SetPixelSize(wx.Size(0, fontSize))
        gc.SetFont(font)
        (width, height) = self.model.GetProperty("size")
        lines = wordwrap(self.model.GetProperty("text"), width, gc)
        extraLineSpacing = 1.25 if wx.Platform == "__WXMSW__" else 1.1
        lineHeight = int(font.GetPixelSize().height * extraLineSpacing)
        return height > lineHeight * len(lines.split('\n'))

    def GetFontSizeFit(self, gc):
        if self.lastFontSize is not None:
            return (self.lastFontSize, self.lastDidShrink)
        fontSize = self.ScaleFontSize(self.model.GetProperty("fontSize"), None)
        if self.DoesTextFitWithSize(gc, fontSize):
            self.lastFontSize = fontSize
            self.lastDidShrink = False
            return (fontSize, False)
        self.lastFontSize = self.FindFittingFontSize(gc, 1, fontSize)
        self.lastDidShrink = True
        return (self.lastFontSize, True)

    def FindFittingFontSize(self, gc, lower, upper):
        fontSize = int((upper + lower) / 2)
        if lower+1 < upper:
            if self.DoesTextFitWithSize(gc, fontSize):
                return self.FindFittingFontSize(gc, fontSize, upper)
            else:
                return self.FindFittingFontSize(gc, lower, fontSize-1)
        else:
            return lower

    def Paint(self, gc):
        align = self.model.GetProperty("alignment")
        (startX, startY) = self.model.GetAbsoluteFrame().BottomLeft
        (width, height) = self.model.GetProperty("size")

        font = wx.Font(self.font)
        didShrink = False
        if self.model.GetProperty("autoShrink"):
            (fontSize, didShrink) = self.GetFontSizeFit(gc)
            if didShrink:
                font.SetPixelSize(wx.Size(0, fontSize))
        gc.SetFont(font)
        gc.SetTextForeground(wx.Colour(self.textColor))
        lines = wordwrap(self.model.GetProperty("text"), width, gc)

        offsetY = 0
        extraLineSpacing = 1.25 if wx.Platform == "__WXMSW__" else 1.1
        lineHeight = int(font.GetPixelSize().height * extraLineSpacing)

        for line in lines.split('\n'):
            line = line.rstrip()
            if align in ["Center", "Right"]:
                textWidth = gc.GetTextExtent(line).Width
                if align == "Center":
                    xPos = startX + (width - textWidth)/2
                else:
                    xPos = startX + width - textWidth
            else:
                xPos = startX
            gc.DrawText(line, wx.Point(xPos, startY-offsetY))
            offsetY += lineHeight
            if offsetY + lineHeight > height:
                break

        if self.stackManager.isEditing:
            if didShrink:
                gc.SetPen(wx.Pen('red', 2, wx.PENSTYLE_DOT))
            else:
                gc.SetPen(wx.Pen('gray', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.model.GetAbsoluteFrame())


class TextLabelModel(TextBaseModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textlabel"
        self.proxyClass = TextLabel
        self.properties["name"] = "label_1"
        self.properties["autoShrink"] = True

        self.propertyTypes["autoShrink"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "autoShrink", "position", "size"]


class TextLabel(TextBaseProxy):
    """
    TextLabel proxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    @property
    def autoShrink(self):
        model = self._model
        if not model: return False
        return model.GetProperty("autoShrink")
    @autoShrink.setter
    def autoShrink(self, val):
        model = self._model
        if not model: return
        model.SetProperty("autoShrink", bool(val))


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
