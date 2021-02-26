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
        self.inlineEditor = None

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

    def StartInlineEditing(self):
        # Show a temporary StyledTextCtrl with the same frame and font as the label
        text = self.model.GetProperty("text")
        alignment = wx.ALIGN_LEFT
        if self.model.GetProperty("alignment") == "Right":
            alignment = wx.ALIGN_RIGHT
        elif self.model.GetProperty("alignment") == "Center":
            alignment = wx.ALIGN_CENTER
        field = stc.StyledTextCtrl(parent=self.stackManager.view, style=alignment | wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
        field.SetUseHorizontalScrollBar(False)
        field.SetUseVerticalScrollBar(False)
        field.SetWrapMode(stc.STC_WRAP_WORD)
        field.SetMarginWidth(1, 0)
        rect = self.view.GetRect().Inflate(1)
        rect.width += 20
        field.SetRect(rect)
        field.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        field.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        field.SetFocus()
        self.UpdateFont(self.model, field)
        field.ChangeValue(text)
        field.EmptyUndoBuffer()
        self.inlineEditor = field
        self.isInlineEditing = True

    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.stackManager.view.SetFocus()
        event.Skip()

    def OnLoseFocus(self, event):
        if self.stackManager.isEditing:
            self.model.SetProperty("text", self.inlineEditor.GetValue())
            self.stackManager.view.RemoveChild(self.inlineEditor)
            wx.CallLater(10, self.inlineEditor.Destroy)
            self.inlineEditor = None
            self.isInlineEditing = False
            self.stackManager.view.Refresh()
        event.Skip()

    def OnResize(self, event):
        self.view.SetLabel(self.model.GetProperty("text"))
        self.view.Wrap(self.view.GetSize().Width)

    def Paint(self, gc):
        if self.stackManager.isEditing:
            gc.SetPen(wx.Pen('Gray', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.model.GetAbsoluteFrame())


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
