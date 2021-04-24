import wx
from uiView import *
from wx.lib.wordwrap import wordwrap
from uiTextBase import *
from killableThread import RunOnMain


class UiTextLabel(UiTextBase):
    """
    This class is a controller that coordinates management of a TextLabel view, based on data from a TextLabelModel.
    """

    def __init__(self, parent, stackManager, model=None):
        if not model:
            model = TextLabelModel(stackManager)
            model.SetProperty("name", stackManager.uiCard.model.GetNextAvailableNameInCard("label"), notify=False)

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
            self.model.SetProperty("text", self.inlineEditor.GetValue(), notify=notify)
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


class TextLabel(TextBaseProxy):
    """
    TextLabel proxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    pass
