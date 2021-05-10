import wx
from commands import SetPropertyCommand
from uiView import *
from uiTextBase import *


class UiTextLabel(UiTextBase):
    """
    This class is a controller that coordinates management of a TextLabel view, based on data from a TextLabelModel.
    """

    def __init__(self, parent, stackManager, model):
        super().__init__(parent, stackManager, model, None)
        self.UpdateFont(model, None)

    def StartInlineEditing(self):
        # Show a temporary StyledTextCtrl with the same frame and font as the label
        text = self.model.GetProperty("text")
        field = stc.StyledTextCtrl(parent=self.stackManager.view, style=wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
        field.SetUseHorizontalScrollBar(False)
        field.SetUseVerticalScrollBar(False)
        field.SetWrapMode(stc.STC_WRAP_WORD)
        field.SetMarginWidth(1, 0)
        rect = self.model.GetAbsoluteFrame().Inflate(1)
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
            command = SetPropertyCommand(True, "Set Property", self, self.stackManager.cardIndex, self.model,
                                         "text", self.inlineEditor.GetValue())
            self.stackManager.command_processor.Submit(command)
            self.stackManager.view.RemoveChild(self.inlineEditor)
            wx.CallAfter(self.inlineEditor.Destroy)
            self.inlineEditor = None
            self.isInlineEditing = False
            self.stackManager.inlineEditingView = None
            self.stackManager.view.SetFocus()
            self.stackManager.view.Refresh()

    def Paint(self, gc):
        align = self.model.GetProperty("alignment")
        (startX, startY) = self.model.GetAbsoluteFrame().BottomLeft
        (width, height) = self.model.GetProperty("size")

        gc.SetFont(self.font)
        gc.SetTextForeground(wx.Colour(self.textColor))
        lines = wordwrap(self.model.GetProperty("text"), width, gc)

        offsetY = 0
        lineHeight = self.font.GetPixelSize().height
        extraLineSpacing = 6 if wx.Platform == "__WXMSW__" else 2

        for line in lines.split('\n'):
            if align in ["Center", "Right"]:
                textWidth = gc.GetTextExtent(line).Width
                if align == "Center":
                    xPos = startX + (width - textWidth)/2
                else:
                    xPos = startX + width - textWidth
            else:
                xPos = startX
            gc.DrawText(line, wx.Point(xPos, startY-offsetY))
            offsetY += lineHeight + extraLineSpacing
            if offsetY + lineHeight >= height:
                break

        if self.stackManager.isEditing:
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


class TextLabel(TextBaseProxy):
    """
    TextLabel proxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    pass

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
