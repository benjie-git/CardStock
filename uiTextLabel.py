import wx
from uiView import *
from uiTextBase import *


class UiTextLabel(UiTextBase):
    """
    This class is a controller that coordinates management of a TextLabel view, based on data from a TextLabelModel.
    """

    def __init__(self, parent, stackManager, model=None):
        if not model:
            model = TextLabelModel(stackManager)
            model.SetProperty("name", stackManager.uiCard.model.GetNextAvailableNameInCard("label_"), False)

        self.stackManager = stackManager
        label = self.CreateLabel(stackManager, model)

        super().__init__(parent, stackManager, model, label)

    def CreateLabel(self, stackManager, model):
        if model:
            text = model.GetProperty("text")
            alignment = wx.ALIGN_LEFT
            if model.GetProperty("alignment") == "Right":
                alignment = wx.ALIGN_RIGHT
            elif model.GetProperty("alignment") == "Center":
                alignment = wx.ALIGN_CENTER
        else:
            text = "Text"
            alignment = wx.ALIGN_LEFT

        label = wx.StaticText(parent=stackManager.view, size=(60,20),
                              style=alignment|wx.ST_NO_AUTORESIZE)
        label.SetLabelText(text)
        self.UpdateFont(model, label)
        return label

    def OnResize(self, event):
        self.view.SetLabel(self.model.GetProperty("text"))
        self.view.Wrap(self.view.GetSize().Width)


class TextLabelModel(TextBaseModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textlabel"
        self.proxyClass = TextLabelProxy


class TextLabelProxy(TextBaseProxy):
    """
    TextLabelProxy objects are the user-accessible objects exposed to event handler code for text label objects.
    """

    pass
