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

    def Paint(self, gc):
        align = self.model.GetProperty("alignment")
        gc.SetFont(self.font)
        gc.SetTextForeground(wx.Colour(self.textColor))
        (width, height) = self.model.GetProperty("size")
        magicExtraWidth = 30  # ?? Not sure why this is needed...
        lines = wordwrap(self.model.GetProperty("text"), width + magicExtraWidth, gc)
        (startX, startY) = self.model.GetAbsoluteFrame().BottomLeft
        offsetY = 0
        extraLineSpacing = 2 if wx.Platform == "__WXMAC__" else 6
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
            offsetY += self.font.GetFractionalPointSize() + extraLineSpacing
            if offsetY + self.font.GetFractionalPointSize() >= height:
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
